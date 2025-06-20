import boto3
import os
import json
import asyncio
import tempfile
from sagemaker.model import Model
from sagemaker.transformer import Transformer
from sagemaker import image_uris
from sagemaker.session import Session

from pinecone import Pinecone, ServerlessSpec

from utils import get_config_from_name, upload_job_to_db, preprocess, upload_batch_to_s3, split_for_threads
from dotenv import load_dotenv
load_dotenv()

S3_BUCKET_VECTOR = os.getenv('S3_BUCKET_VECTOR')
SAGEMAKER_ROLE = os.getenv('SAGEMAKER_ROLE')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GPU_INSTANCE_MAPPING = {
    'T4': 'ml.g4dn.xlarge',
    'A10G': 'ml.g5.xlarge',
    'A100': 'ml.p4d.24xlarge',
    'H100': 'ml.p5.48xlarge'
}



def download_outputs_from_s3(bucket, prefix):
    s3 = boto3.client('s3')
    local_dir = tempfile.mkdtemp()
    downloaded_files = []

    result = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    for obj in result.get('Contents', []):
        print(obj['Key'])
        key = obj['Key']
        if not key.endswith('.json.out'):
            continue
        local_path = os.path.join(local_dir, os.path.basename(key))
        s3.download_file(bucket, key, local_path)
        downloaded_files.append(local_path)

    return downloaded_files




def upload_embeddings_to_pinecone(index_name, vectors):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=len(vectors[0]['embedding']),
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )

    index = pc.Index(index_name)
    upserts = [(str(v["id"]), v["embedding"], {"text": v["text"]}) for v in vectors]
    index.upsert(vectors=upserts)

    
    

async def run_inference_job(job_name, model, data, username, config_name):

    config = await get_config_from_name(config_name, username)
    regex_pattern = config['regexpattern']
    regex_replacement = config['regexreplacement']
    gpu_type = config['gpu']
    instance_count = config.get('num_workers', 10)
    batch_size = config.get('batch_size', 100)

    instance_type = GPU_INSTANCE_MAPPING.get(gpu_type)
    if not instance_type:
        raise ValueError(f"Invalid GPU type: {gpu_type}")


    input_s3_prefix = f"batch_jobs/{username}/{job_name}/"

    batch_idx = 0
    total_chunks_uploaded = 0

    while not data.data_finished:
        raw_batch = await data.get_batch()
        preprocessed_batch = preprocess(
            raw_batch, tok_limit=512,
            regexPattern=regex_pattern, regexReplacement=regex_replacement
        )

        chunk_list = split_for_threads(preprocessed_batch, instance_count)

        for idx, chunk in enumerate(chunk_list):
            s3_key = f"{input_s3_prefix}chunk_{batch_idx}_{idx}.json"
            upload_batch_to_s3(S3_BUCKET_VECTOR, s3_key, chunk)
            total_chunks_uploaded += 1

        batch_idx += 1


    image_uri = image_uris.retrieve(
        framework='huggingface',
        region=AWS_REGION,
        version='4.26.0',
        base_framework_version='pytorch1.13.1',
        instance_type=instance_type,
        image_scope='inference',
        py_version='py39'
    )


    boto_session = boto3.Session(region_name=AWS_REGION)
    sagemaker_session = Session(boto_session=boto_session)

    # Step 4: Create SageMaker Model
    model_name = f"{username}-{job_name}-model"
    embedding_model = Model(
        model_data=f's3://{S3_BUCKET_VECTOR}/models/model.tar.gz',
        role=SAGEMAKER_ROLE,
        image_uri=image_uri,
        sagemaker_session=sagemaker_session
    )

    embedding_model.name = model_name
    embedding_model.create(instance_type=instance_type)

    # Step 5: Launch Batch Transform
    transformer = Transformer(
        model_name=model_name,
        instance_count=instance_count,
        instance_type=instance_type,
        strategy='MultiRecord',
        assemble_with='Line',
        output_path=f's3://{S3_BUCKET_VECTOR}/batch_output/{username}/{job_name}/',
        accept='application/json',
        sagemaker_session=sagemaker_session
    )

    transformer.transform(
        data=f's3://{S3_BUCKET_VECTOR}/{input_s3_prefix}',
        content_type='application/json',
        split_type='Line',
        wait=False 
    )

    transform_job_name = transformer.latest_transform_job.name
    sagemaker_session.wait_for_transform_job(transform_job_name)
    print(f"SageMaker Batch Transform job launched for {job_name}")
    
    print("Getting final files")
    output_s3_prefix = f"batch_output/{username}/{job_name}/"
    output_files = download_outputs_from_s3(S3_BUCKET_VECTOR, output_s3_prefix)
    embeddings = []
    for file_path in output_files:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    embeddings.append(json.loads(line.strip()))

    print("Uploading to pinecone")
    pinecone_index = f"{username}-{job_name}"
    upload_embeddings_to_pinecone(pinecone_index, embeddings)

    await upload_job_to_db(job_name, config_name, username)
    print("Job metadata saved to DB")

    return True