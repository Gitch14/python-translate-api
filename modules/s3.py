import boto3
import logging
import os
import time
import sys
from botocore.exceptions import ClientError
from dotenv import load_dotenv
load_dotenv()


def s3_connect():
    boto3.setup_default_session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )
    for attempt in range(int(os.getenv("S3_CONNECTION_ATTEMPTS_COUNT"))):
        try:
            client = boto3.resource('s3')
            logging.warning(f"Successfully connected to S3 bucket")
            return client
        except Exception as e:
            logging.warning(f'Unable to connect to S3 -> {e}')
            logging.warning(f'I wait {os.getenv("S3_CONNECTION_TIMEOUT")} seconds and connect again...')
            time.sleep(int(os.getenv("S3_CONNECTION_TIMEOUT")))
        if attempt == int(os.getenv("S3_CONNECTION_ATTEMPTS_COUNT")) - 1:
            logging.warning('Shutdown...')
            sys.exit(1)


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


def put_file(client, bucket, file_name, image_data):
    try:
        client.Bucket(bucket).put_object(Key=file_name, Body=image_data)
        return True
    except Exception as e:
        print(e)
        logging.warning("File upload error")
        return False


def delete_file(client, bucket, file_name):
    client.Object(bucket, file_name).delete()


def check_exist(client, bucket, file_name):
    try:
        client.Object(bucket, file_name).load()
        return True
    except client.meta.client.exceptions.NoSuchKey:
        return False


def download_file(client, bucket, object_name, file_name):
    try:
        client.Bucket(bucket).Object(object_name).download_file(file_name)
        return True
    except Exception as e:
        print(e)
        logging.warning("File download error")
        return False


if __name__ == "__main__":
    client = s3_connect()
    # for bucket in client.buckets.all():
    #     print(bucket.name)
    bucket_name = "recipetestbucket"
    # delete_file(client, bucket_name, "/None/None/Step 1.png")

    bucket = client.Bucket(bucket_name)
    for obj in bucket.objects.all():
        print(f"Name {obj.key}")
        # print(f"Size {obj.size}")
        # print(f"Date {obj.key}")
    # download_file(client, bucket_name, "/user-1/recipe-1/Step 1.png", "Step 1.png")
