from minio import Minio

client = Minio( "s3.eai.dziubalabs.de", secure=True)
objects = client.list_objects("yatai", prefix="bentos/default/wf_classifier", recursive=True)
objects = sorted(objects, key=lambda obj: obj.last_modified, reverse=True)
latest_object = objects[0]
bento_tag = latest_object.object_name.split('/')[-1].split('.')[0]

print(bento_tag)
