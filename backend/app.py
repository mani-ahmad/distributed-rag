from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_cors import CORS
import os
import json
import boto3
import db as database
from bedrock import *

from dotenv import load_dotenv

from utils import *
from MultiInfer import run_inference_job

app = Flask(__name__)
CORS(app)
load_dotenv()


AWS_REGION = os.getenv('AWS_REGION', 'ap-south-1')
S3_BUCKET_NAME_FILE_UPLOAD = os.getenv('S3_BUCKET_NAME_FILE_UPLOAD', 'your-drag-data-bucket')
PC_API_KEY = os.getenv('PINECONE_API_KEY')
s3_client = boto3.client('s3', region_name=AWS_REGION)

@app.route('/')
def root():
    return jsonify({"message":"success"}), 200

# ------------------------------------------------ Login / Signup -----------------------------------------------------
@app.route('/add_user', methods=['GET', 'POST'])
async def signup():
    if request.method == 'POST':
        data = request.json
        username = data['username']
        
        message, isSuccess = await add_user(username)
        if isSuccess:
            return jsonify({"message":message}), 200
        else: 
            return jsonify({'error': message}), 500

# -------------------------------------------------- Data Uploading on S3 ----------------------------------------------

@app.route('/get_local_data_list', methods=['POST'])
async def get_local_data_list():
    data = request.json
    print(data)
    username = data['username']
    print(username)

    if username == '':
        return jsonify({'error': 'User not logged in'}), 403

    prefix = f'local_data/{username}/'

    try:
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME_FILE_UPLOAD, Prefix=prefix)
        files = []
        if 'Contents' in response:
            files = [obj['Key'].replace(prefix, '') for obj in response['Contents'] if obj['Key'].endswith('.zip')]

        return jsonify({'files': files}), 200
    except Exception as e:
        print(f"Error listing files from S3: {e}")
        return jsonify({'error': 'Failed to list files'}), 500


@app.route('/upload_local_data', methods=['POST'])
async def upload_local_data():
    try:
        file = request.files['file']
        file_name = request.form['name']
        username = request.form['username']

        if username == '':
            return jsonify({'error': 'User not logged in'}), 403

        s3_key = f'local_data/{username}/{file_name}.zip'

        s3_client.upload_fileobj(file, S3_BUCKET_NAME_FILE_UPLOAD, s3_key)
        return jsonify({'message': 'File uploaded successfully'}), 200

    except Exception as e:
        print(f"Error in /upload_local_data: {e}")
        return jsonify({'error': f'Failed to upload file: {str(e)}'}), 500

# -------------------------------------------------------- Config -----------------------------------------------------------


@app.route('/save_config', methods=['POST'])
async def save_config():
    conn = await database.connectDatabase()
    config = request.json

    name = config['configName']
    gpu = config['gpu']
    embedding_model = config['embeddingModel']
    batch_size = config['batchSize']
    regexPattern = config['regexPattern']
    regexReplacement = config['regexReplacement']
    username = config['username']
    num_workers = config['num_workers']

    try:
        await conn.execute('''
            INSERT INTO configurations (config_name, gpu, embedding_model, num_workers, batch_size, regexPattern, regexReplacement, username) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ''', name, gpu, embedding_model, num_workers, batch_size, regexPattern, regexReplacement, username)
        
        return jsonify({'message': 'Config saved successfully'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'An error occurred: ' + str(e)}), 500

@app.route('/get_config_list', methods=['POST'])
async def get_config_list():
    # Extract username from request body
    data = request.get_json()
    username = data.get('username')

    conn = await database.connectDatabase()
    # Use username in SQL query
    records = await conn.fetch('SELECT config_name FROM configurations WHERE username = $1', username)
    
    # Extract config_name from each record
    configs = [record['config_name'] for record in records]

    return jsonify({'configs': configs}), 200



# ----------------------------------------------- Distributed Vectorization -------------------------------------

async def load_config(config_name):
    conn = await database.connectDatabase()
    record = await conn.fetchrow('SELECT * FROM configurations WHERE config_name = $1', config_name)
    return dict(record)


@app.route('/run_job', methods=['POST'])
async def run_job():
    try:
        print("Got job request")
        data = request.json

        config_name = data['config']
        data_name = data['data'] #file name 
        job_name = data['job_name']
        username = data['username']
        data_source_type = data['data_source_type']
        
        config = await load_config(config_name)
        batch_size = config['batch_size']

        datasrc = await get_data_from_source(data_source_type, data_name, username, batch_size)

        print(config)

        model = config['embedding_model']

        resp = await run_inference_job(job_name, model, datasrc, username, config_name)

        return jsonify({'message': 'Job completed successfully'}), 200
    except Exception as e:
        print(e)
        raise e
        return jsonify({'message': 'Job failed: ' + str(e)}), 500

@app.route('/get_models_list', methods=['GET'])
async def get_models_list():
    with open('models.json') as f:
        models = json.load(f)
    return jsonify({'models': models}), 200


@app.route('/get_jobs', methods=['POST'])
async def get_jobs():
    data = request.get_json()
    username = data.get('username')

    jobs = await get_jobs_from_db(username)
    ret = []
    for job in jobs:
        ret.append({
            'id': dict(job)['job_id'],
            'name': dict(job)['job_name'],
            'date': dict(job)['job_start_time'],
            'expanded': False
        })
    return jsonify(ret), 200


@app.route('/delete_job', methods=['POST'])
async def delete_job():
    data = request.json
    print(data)
    job_name = data['name']
    username = data['username']

    try:
        await delete_job_from_db(job_name, username)
        delete_index(job_name, username, PC_API_KEY)
        return jsonify({'message': 'Job deleted successfully'}), 200
    
    except Exception as e:
        print("==============")
        print(e)
        print("==============")
        return jsonify({'message': 'Job deletion failed'}), 500
    
    
@app.route('/export_docs', methods=['POST'])
def export_docs():
    try:
        data = request.get_json()
        job_name = data.get('job_name')
        search_endpoint = data.get('search_endpoint')
        chat_endpoint = data.get('chat_endpoint')

        with open('doc_template.md') as f:
            md_template = f.read()

        md_template = md_template.replace('''{JOB_NAME}''', job_name)
        md_template = md_template.replace('''{SEARCH_ENDPOINT}''', search_endpoint)
        md_template = md_template.replace('''{CHAT_ENDPOINT}''', chat_endpoint)

        return jsonify({'message': 'Exporting Successful', 'md': md_template}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': f'Exporting Failed: {str(e)}'}), 500

# -------------------------------------------------------- TODO: Endpoints -----------------------------------------------------------

@app.route('/search/<id>', methods=['POST'])
async def search(id):
    data = request.get_json()
    n = data.get('n')
    query = data.get('query')
    filters = data.get('filters')
    username = data.get('username')
    job_name = await get_job_name_from_id(id)

    result = await search_index(PC_API_KEY, username, job_name, query, n, filters)
    result = result.to_dict()['matches']

    print("Type of result: ", type(result))

    return jsonify(result), 200

    ''' a POST endpoint for querying the chat endpoint, takes in 
    | n              | int       | Determines the number of search results returned                                                                            |
    | search_query   | string    | Query that will be used for the similarity search for retrieval purposes                                                    |
    | chat_query     | string    | Query that will be fed to the LLM to get a response based on the retrieved context                                          |
    | system_message | string    | System Message for the LLM for customization purposes, defaults to empty string                                             |
    | model          | string    | one of 'gpt-3.5' or 'gpt-4' (only OpenAI models are supported for now)                                                      |
    | filters        | object    | object with key value pairs, where each key is the attribute to filter on, and value is the filter value for that attribute |
    and gets index name using /chat/:id'''

@app.route('/chat/<id>', methods=['POST'])
async def chat(id):
    data = request.get_json()
    n = data.get('n')
    search_query = data.get('search_query')
    chat_query = data.get('chat_query')
    system_message = data.get('system_message', '')
    username = data.get('username')
    filters = data.get('filters')

    try:

        job_name = await get_job_name_from_id(id)
        result = await search_index(PC_API_KEY, username, job_name, search_query, n, filters)
        context_docs = result.to_dict()['matches']
        
        full_prompt = build_chat_prompt(context_docs, chat_query)
        print(f"Querying Mistral with job_name: {job_name}")
        print(f"Chat query: {chat_query}")
        response = query_mistral(full_prompt, system_message=system_message, max_tokens=4096)
        
        return jsonify({'answer': response}), 200
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'answer': f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
