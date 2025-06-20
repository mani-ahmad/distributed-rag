import os
import re
import boto3
import json
import io
import db as database
from datetime import datetime
from DataSource import DataSource
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
s3_client = boto3.client('s3')
client = OpenAI(api_key=OPENAI_API_KEY)

async def get_data_from_source(src_type, name, username, batch_size=100):
    if batch_size is None or batch_size == '':
        batch_size = 100

    if src_type == 'local':
        return DataSource(src_type, name, username, batch_size)
    else:
        raise ValueError("Only 'local' data source (from S3) is supported now.")

async def get_config_from_name(config_name, username):
    db = await database.connectDatabase()

    try:
        stmt = await db.prepare("SELECT * FROM configurations WHERE config_name = $1 AND username = $2")
        record = await stmt.fetchrow(config_name, username)
        config = dict(record)
        return config
    except Exception as error:
        print(f"Error while fetching config: {error}")
        return False
    
async def upload_job_to_db(job_name, config_name, username):
    db = await database.connectDatabase()

    try:
        stmt = await db.prepare("SELECT config_id FROM configurations WHERE config_name = $1")
        config_id = await stmt.fetchval(config_name)

        stmt = await db.prepare("SELECT id FROM users WHERE username = $1")
        user_id = await stmt.fetchval(username)

        stmt = await db.prepare("INSERT INTO job_details (job_name, config_id, user_id, job_start_time) VALUES ($1, $2, $3, $4)")
        await stmt.fetch(job_name, config_id, user_id, datetime.now())

        return True
    except Exception as error:
        print(f"Error while uploading job to db: {error}")
        return False
    
def preprocess(data, tok_limit, regexPattern='', regexReplacement=''):
    chunks = []

    for doc in data:
        doc_name = doc["name"]
        doc_text = doc["text"]
        chunk_id = 0

        if regexPattern and regexReplacement:
            doc_text = re.sub(regexPattern, regexReplacement, doc_text)

        if len(doc_text) <= tok_limit:
            chunks.append({"name": doc_name, "text": doc_text, "chunk_id": chunk_id})
        else:
            for i in range(0, len(doc_text), tok_limit):
                chunk_id += 1
                chunks.append({"name": doc_name, "text": doc_text[i:i+tok_limit], "chunk_id": chunk_id})

    return chunks

def split_for_threads(chunks, num_threads=30):
    n = len(chunks)
    k, m = divmod(n, num_threads)
    return [chunks[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(num_threads)]


def upload_batch_to_s3(bucket_name, s3_key, batch_data):
    import io
    import boto3
    import json

    s3_client = boto3.client('s3')
    buffer = io.StringIO()

    for idx, doc in enumerate(batch_data):
        text = doc.get("text", "").replace("\n", " ").strip()
        if not text:
            continue

        json_line = json.dumps({
            "id": idx + 1,
            "inputs": text
        })
        buffer.write(json_line + "\n")

    buffer.seek(0)
    content = buffer.getvalue()

    if not content.strip():
        print(f"⚠️ Skipped upload: chunk {s3_key} was empty")
        return

    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_key,
        Body=content,
        ContentType='application/json'
    )

    print(f"Uploaded batch to s3://{bucket_name}/{s3_key}")




async def signup(username, password):
    db = await database.connectDatabase()
    hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), SALT.encode('utf-8'), 100000)

    try:
        # Prepare the statement to check if the user already exists
        stmt = await db.prepare("SELECT username FROM users WHERE username = $1")
        result = await stmt.fetchrow(username)
        
        if result:
            return "User already exists", False

    except Exception as error: 
        return str(error), False

    try:
        # Prepare the statement for inserting a new user
        stmt = await db.prepare("INSERT INTO users (username, password) VALUES ($1, $2)")
        await stmt.fetch(username, hashed_password)
        return "success", True
    except Exception as error: 
        return str(error), False
    
    
async def add_user(username: str):
    db = await database.connectDatabase()
    try:
        stmt = await db.prepare("INSERT INTO users (username) VALUES ($1)")
        await stmt.fetch(username)
        return "success", True
    except Exception as error: 
        return str(error), False
    
async def get_user_id_from_username(username):
    db = await database.connectDatabase()

    try:
        stmt = await db.prepare("SELECT id FROM users WHERE username = $1")
        user_id = await stmt.fetchval(username)
        return user_id
    except Exception as error:
        print(f"Error while fetching user id: {error}")
        return False

async def get_jobs_from_db(username):
    db = await database.connectDatabase()

    try:
        user_id = await get_user_id_from_username(username)
        stmt = await db.prepare("SELECT job_id, job_name, job_start_time FROM job_details WHERE user_id = $1 ORDER BY job_start_time DESC")
        jobs = await stmt.fetch(user_id)
        return jobs
    
    except Exception as error:
        print(f"Error while fetching jobs: {error}")
        return False
    
async def get_job_name_from_id(job_id):
    db = await database.connectDatabase()

    try:
        stmt = await db.prepare("SELECT job_name FROM job_details WHERE job_id = $1")
        job_name = await stmt.fetchval(int(job_id))
        return job_name
    except Exception as error:
        print(f"Error while fetching job name: {error}")
        return False

async def delete_job_from_db(job_name, username):
    db = await database.connectDatabase()
    try:
        user_id = await get_user_id_from_username(username)
        stmt = await db.prepare("DELETE FROM job_details WHERE job_name = $1 AND user_id = $2")
        await stmt.fetch(job_name, user_id)
        return True
    except Exception as error:
        print(f"Error while deleting job: {error}")
        return False
    
    
def build_chat_prompt(context_docs, user_query):
    context_docs = [doc["metadata"]["text"]for doc in context_docs]
    context_string = "\n\n".join(context_docs)
    prompt = f"""
    Using the following context, answer the question as best as you can:

    Context:
    {context_string}

    Question:
    {user_query}
    """
    return prompt 

def delete_index(job_name, username, api_key):
    pc = Pinecone(api_key=api_key)
    pc.delete_index(f"{username}-{job_name}")
    return True


def normalize_l2(x):
    x = np.array(x)
    if x.ndim == 1:
        norm = np.linalg.norm(x)
        if norm == 0:
            return x
        return x / norm
    else:
        norm = np.linalg.norm(x, 2, axis=1, keepdims=True)
        return np.where(norm == 0, x, x / norm)

def get_single_embedding(query: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
        encoding_format="float"
    )

    raw_vector = response.data[0].embedding[:384]
    normalized_vector = normalize_l2(raw_vector)

    return normalized_vector.tolist()


async def get_model_from_job(job_name):
    db = await database.connectDatabase()

    try:
        stmt = await db.prepare("SELECT config_id FROM job_details WHERE job_name = $1")
        config_id = await stmt.fetchval(job_name)

        stmt = await db.prepare("SELECT embedding_model FROM configurations WHERE config_id = $1")
        model = await stmt.fetchval(config_id)

        return model

    except Exception as error:
        print(f"Error while fetching model: {error}")
        return False
    
async def search_index(api_key, username, job_name, query, n=5, filters=None):
    pc = Pinecone(api_key=api_key)
    index = pc.Index(f"{username}-{job_name}")

    print("Fetching from remote")
    vector = get_single_embedding(query)

    print(vector)

    results = index.query(vector=vector, top_k=n, filters=filters, include_metadata=True)

    return results