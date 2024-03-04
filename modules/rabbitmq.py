import pika
import time
import sys
import logging
import os
import json
from modules.db import create_user, create_recipe, create_step
from dotenv import load_dotenv
load_dotenv()

queues = ["recipeServiceCreate", "recipeServiceUpdate", "recipeServiceRemove", "recipeServiceStatus",
          "registrationService"]
connection_to_db = None


def connect_to_rabbitmq(connection_db=None):
    global connection_to_db
    if connection_db is not None:
        connection_to_db = connection_db
    for attempt in range(int(os.getenv('RABBITMQ_CONNECTION_ATTEMPTS_COUNT'))):
        try:
            credentials = pika.PlainCredentials(os.getenv('RABBITMQ_USERNAME'), os.getenv('RABBITMQ_PASSWORD'))
            connection = pika.BlockingConnection(pika.ConnectionParameters(os.getenv('RABBITMQ_HOST'), os.getenv('RABBITMQ_PORT'), "/", credentials))
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
        create_user(connection_to_db, message["email"], message["name"], message["password"])
        logging.warning(f"NEW USER SUCCESSFULLY CREATED")
    elif method.routing_key == "recipeServiceCreateRoutingKey":
        # with open("create_recipe.json", "w") as file:
        #     json.dump(message, file, indent=4)
        create_recipe(connection_to_db, message["title"], message["description"], message["type"], message["imagePath"],
                      message["videoPath"], message["optional"], message["datePublish"],
                      message["timeToCookAndPreparing"], message["timeToCook"], message["timeToPreparing"],
                      message["difficulty"], message["calories"], message["proteins"], message["carbohydrates"],
                      message["fats"], message["author"])
        for step in message["steps"]:
            create_step(connection_to_db, step["recipe"], step["stepNumber"], step["stepName"],
                        step["imagePath"] if len(step["imagePath"]) < 255 else step["imagePath"][0:255], step["text"])


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
