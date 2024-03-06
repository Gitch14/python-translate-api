import pika
import time
import sys
import logging
import os
import json
from modules.db import create_user, create_recipe
from dotenv import load_dotenv
load_dotenv()

queues = ["recipeServiceCreate", "recipeServiceUpdate", "recipeServiceRemove", "recipeServiceStatus",
          "registrationService"]
connection_to_db = None
s3_client = None


def connect_to_rabbitmq(connection_db=None, s3=None):
    global connection_to_db, s3_client
    if connection_db is not None:
        connection_to_db = connection_db
    if s3 is not None:
        s3_client = s3
    for attempt in range(int(os.getenv('RABBITMQ_CONNECTION_ATTEMPTS_COUNT'))):
        try:
            credentials = pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                os.getenv('RABBITMQ_HOST'), os.getenv('RABBITMQ_PORT'), "/", credentials))
            logging.warning("Successfully connected to the RabbitMQ server")
            return connection
        except Exception as e:
            logging.warning(e)
            logging.warning("I can`t connect to the RabbitMQ server!!!")
            logging.warning(f"I wait {os.getenv('RABBITMQ_CONNECTION_TIMEOUT')} seconds and connect again...")
            time.sleep(int(os.getenv('RABBITMQ_CONNECTION_TIMEOUT')))
        if attempt == int(os.getenv('RABBITMQ_CONNECTION_ATTEMPTS_COUNT')) - 1:
            logging.warning("Shutdown...")
            sys.exit(1)


def on_message(ch, method, properties, body):
    logging.warning(f"Message - {json.loads(body)} by channel {method.routing_key}")
    message = json.loads(body)

    if method.routing_key == "registrationServiceRoutingKey":
        # create_user(connection_to_db, message["email"], message["name"], message["password"])
        result = create_user(connection_to_db, message)
        if result is True:
            logging.warning(f"NEW USER SUCCESSFULLY CREATED")
        elif result == "User already exists":
            logging.warning(f"THIS USER IS EXISTS -> {message["email"]}")
        else:
            logging.warning(f"Error -> rabbitmq.py")

    elif method.routing_key == "recipeServiceCreateRoutingKey":
        result = create_recipe(connection_to_db, s3_client, message)
        if result:
            logging.warning(f"NEW RECIPE SUCCESSFULLY CREATED")
        else:
            logging.warning(f"Error -> rabbitmq.py")

        with open("create_recipe.json", "w") as file:
            json.dump(message, file, indent=4)


def declare_and_consume_queues(connection: pika.BlockingConnection, queues):
    channel = connection.channel()
    for queue in queues:
        channel.queue_declare(queue)
        channel.basic_consume(queue, on_message_callback=on_message, auto_ack=True)
    return channel


if __name__ == "__main__":
    # print(f"RabbitMQ user - {os.getenv("RABBITMQ_USERNAME")} \nRabbitMQ password - {os.getenv("RABBITMQ_PASSWORD")}")
    # print(f"Type of con timeout - {isinstance(int(os.getenv('RABBITMQ_CONNECTION_TIMEOUT')), int)}")

    connection = connect_to_rabbitmq()
    channel = declare_and_consume_queues(connection, queues)
    channel.start_consuming()
