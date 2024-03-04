import boto3
import logging
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()


def init_s3_client():
    boto3.setup_default_session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    try:
        client = boto3.resource('s3')
        return client
    except Exception as e:
        print(e)
        logging.warning('Unable to connect to S3')


def upload_file(client, bucket, file_name, object_name=None):
    if object_name is None:
        object_name = file_name
    try:
        client.Bucket(bucket).Object(object_name).upload_file(file_name)
        return True
    except Exception as e:
        print(e)
        logging.warning("File upload error")
        return False


def download_file(client, bucket, object_name, file_name=None):
    if file_name is None:
        file_name = object_name
    try:
        client.Bucket(bucket).Object(object_name).download_file(file_name)
        return True
    except Exception as e:
        print(e)
        logging.warning("File download error")
        return False


if __name__ == "__main__":
    client = init_s3_client()
    # for bucket in client.buckets.all():
    #     print(bucket.name)