import os
from minio import Minio
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('./container/.env')
load_dotenv(dotenv_path=dotenv_path)
s3_url = os.getenv("S3_URL")

client = Minio( s3_url, secure=True)
objects = client.list_objects("yatai", prefix="bentos/default/wf_service", recursive=True)
objects = sorted(objects, key=lambda obj: obj.last_modified, reverse=True)
latest_object = objects[0]
bento_tag = latest_object.object_name.split('/')[-1].split('.')[0]

print(bento_tag)
