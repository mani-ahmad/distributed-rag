import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

MODEL = "mistral.mistral-small-2402-v1:0"
REGION = os.getenv('AWS_REGION', 'us-east-1')

def query_mistral(prompt, system_message="", max_tokens=4096, temperature=0.5):
    bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=REGION
            )
    
    body = {
        "prompt": system_message + '\n\n' + prompt,
        "max_tokens": max_tokens,
        "temperature": 0.5
    }
    
    response = client.invoke_model(
        modelId=MISTRAL_SMALL_MODEL_ID,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json"
    )
    
    try: 
        return response['body']["outputs"][0]['text']
    except: 
        return ""
    
    
    