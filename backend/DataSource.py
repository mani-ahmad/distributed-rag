import boto3
import io
import zipfile
import os
from dotenv import load_dotenv
load_dotenv()

AWS_REGION = os.getenv('AWS_REGION')
S3_BUCKET_NAME_FILE_UPLOAD = os.getenv('S3_BUCKET_NAME_FILE_UPLOAD')
s3_client = boto3.client('s3', region_name=AWS_REGION)

class DataSource:
    def __init__(self, src_type, src_name, username, batch_size=100):
        self.src_type = src_type
        self.src_name = src_name
        self.batch_size = batch_size
        self.batch_index = 0
        self.data_finished = False
        self.username = username
        self.s3_key = f'local_data/{self.username}/{self.src_name}'

        self.namelist = None 
        self.zipfile_obj = None

    async def get_batch(self):
        if self.src_type != 'local':
            raise ValueError("Invalid source type. Only 'local' (S3) is supported.")

        return await self.get_local_batch()

    async def get_local_batch(self):
        if self.zipfile_obj is None:
            await self._load_zip_from_s3()

        datasrc = []
        namelist_slice = self.namelist[self.batch_index:self.batch_index + self.batch_size]

        if not namelist_slice:
            self.data_finished = True
            return []

        for filename in namelist_slice:
            with self.zipfile_obj.open(filename) as f:
                try:
                    datasrc.append({
                        'name': filename,
                        'text': f.read().decode('utf-8')
                    })
                except UnicodeDecodeError:
                    print(f"Skipping non-text file: {filename}")

        self.batch_index += self.batch_size

        if self.batch_index >= len(self.namelist):
            self.data_finished = True

        return datasrc

    async def _load_zip_from_s3(self):
        print(f"Downloading zip from S3: {self.s3_key}")

        response = s3_client.get_object(Bucket=S3_BUCKET_NAME_FILE_UPLOAD, Key=self.s3_key)
        zip_content = response['Body'].read()

        self.zipfile_obj = zipfile.ZipFile(io.BytesIO(zip_content))
        self.namelist = self.zipfile_obj.namelist()
