# import pika
# import psycopg2
# import json
# import sys
# import signal
# import logging
# import time
# import boto3
# from botocore.exceptions import ClientError
# import os
# from dotenv import load_dotenv
# load_dotenv()
#
# boto3.setup_default_session(
#     aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#     aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
# )
#
# queues = ["recipeServiceCreate", "recipeServiceUpdate", "recipeServiceRemove", "recipeServiceStatus"]
# con_db = None
# con_pika = None
# count_try = 0
#
#
# def connect_to_database():
#     global con_db, count_try
#     try:
#         con_db = psycopg2.connect(
#             dbname="manga_translation_db",
#             user="admin",
#             password="admin1234",
#             host="postgres",
#             port="5432"
#         )
#         logging.warning("Successfully connected to the database")
#         count_try = 0
#     except Exception as e:
#         print(e)
#         logging.warning("I can`t connect to the database!!!")
#         logging.warning("I wait 30 seconds and connect again...")
#         count_try += 1
#         if count_try == 3:
#             sys.exit(1)
#         time.sleep(30)
#         connect_to_database()
#
#
# def connect_to_rabbitmq():
#     global con_pika, count_try
#     try:
#         con_pika = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", 5672, "/", pika.PlainCredentials("user", "111")))
#         logging.warning("Successfully connected to the rabbitmq server")
#         count_try = 0
#     except Exception as e:
#         print(e)
#         logging.warning("I can`t connect to the rabbitmq server!!!")
#         logging.warning("I wait 30 seconds and connect again...\n")
#         count_try += 1
#         if count_try == 3:
#             sys.exit(1)
#         time.sleep(30)
#         connect_to_rabbitmq()
#
#
# def on_message(ch, method, properties, body):
#     # print(f"Сообщение - {body}; получено с канала - {method.routing_key}")
#     logging.warning(f"Message - {json.loads(body)} by channel {method.routing_key}")
#
#
# def upload_file(file_name, bucket, object_name=None):
#     if object_name is None:
#         object_name = os.path.basename(file_name)
#
#     s3_client = boto3.client('s3')
#     try:
#         response = s3_client.upload_file(file_name, bucket, object_name)
#     except Exception as e:
#         logging.error(e)
#         return False
#     return True
#
#
# def download_file(file_name, bucket):
#     s3_client = boto3.client('s3')
#     s3_client.download_file(bucket, file_name, file_name)
#
#
# def delete_file(file_name, bucket):
#     s3_client = boto3.client('s3')
#     s3_client.delete_object(Bucket=bucket, Key=file_name)
#
#
# def check_file(file_name, bucket):
#     s3_client = boto3.client('s3')
#
#     try:
#         s3_client.head_object(Bucket=bucket, Key=file_name)
#         print(f"Файл {file_name} существует в бакете {bucket}")
#     except ClientError as e:
#         print(f"Файл {file_name} не существует а бакете {bucket}")
#
#
# def main():
#     # print("Start app....")
#     logging.warning("Starting up...")
#
#     def signal_handler(sig, frame):
#         logging.info("Shutdown...")
#         channel.close()
#         con_pika.close()
#         sys.exit(0)
#
#     signal.signal(signal.SIGINT, signal_handler)
#
#     connect_to_database()
#     connect_to_rabbitmq()
#
#     channel = con_pika.channel()
#
#     channel.queue_declare(queues[0])
#     channel.queue_declare(queues[1])
#     channel.queue_declare(queues[2])
#
#     channel.basic_consume(queue=queues[0], on_message_callback=on_message, auto_ack=True)
#     channel.basic_consume(queue=queues[1], on_message_callback=on_message, auto_ack=True)
#     channel.basic_consume(queue=queues[2], on_message_callback=on_message, auto_ack=True)
#
#     # create_tables()
#     channel.start_consuming()
#
#
# if __name__ == "__main__":
#     main()
#     # s3 = boto3.resource("s3")
#     # for bucket in s3.buckets.all():
#     #     print(bucket.name)
#     # upload_file("test.txt", "recipetestbucket", "test.txt")
#     # download_file("test.txt", "recipetestbucket")
#     # delete_file("test.txt", "recipetestbucket")
#     # check_file("test.txt", "recipetestbucket")

from rabbitmq import connect_to_rabbitmq, declare_and_consume_queues
from rabbitmq import queues
from db import connect_to_db
from image import image_to_base64, base64_to_image


def main():
    connection_db = connect_to_db()
    connection_pika = connect_to_rabbitmq(connection_db)
    channel = declare_and_consume_queues(connection_pika, queues)

    channel.start_consuming()


if __name__ == "__main__":
    main()

    # with open("test-image.jpg", "rb") as image_file:
    #     image_bytes = image_file.read()

    # base64_image = base64.b64encode(image_bytes)
    # base64_image_str = base64_image.decode('utf-8')

    # print(image_to_base64(image_bytes))
    #
    # with open("new-image.jpg", "wb") as image_file:
    #     image_file.write(base64_to_image(image_to_base64(image_bytes)))
