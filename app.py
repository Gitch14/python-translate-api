import pika
import psycopg2
import json
import sys
import signal
import logging
import time


queues = ["recipeServiceCreate", "recipeServiceUpdate", "recipeServiceRemove", "recipeServiceStatus"]
con_db = None
con_pika = None
count_try = 0


def connect_to_database():
    global con_db, count_try
    try:
        con_db = psycopg2.connect(
            dbname="manga_translation_db",
            user="admin",
            password="admin1234",
            host="postgres",
            port="5432"
        )
        logging.warning("Successfully connected to the database")
        count_try = 0
    except Exception as e:
        print(e)
        logging.warning("I can`t connect to the database!!!")
        logging.warning("I wait 30 seconds and connect again...\n")
        count_try += 1
        if count_try == 3:
            sys.exit(1)
        time.sleep(30)
        connect_to_database()


def connect_to_rabbitmq():
    global con_pika, count_try
    try:
        con_pika = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", 5672, "/", pika.PlainCredentials("user", "111")))
        logging.warning("Successfully connected to the rabbitmq server")
        count_try = 0
    except Exception as e:
        print(e)
        logging.warning("I can`t connect to the rabbitmq server!!!")
        logging.warning("I wait 30 seconds and connect again...\n")
        count_try += 1
        if count_try == 3:
            sys.exit(1)
        time.sleep(30)
        connect_to_rabbitmq()

def create_tables():
    cursor = con_db.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS cook (cook_id INTEGER PRIMARY KEY NOT NULL, first_name VARCHAR(128) NOT NULL, last_name VARCHAR(128) NOT NULL);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS recipe (recipe_id INTEGER PRIMARY KEY NOT NULL, title VARCHAR(255) NOT NULL, descripion TEXT NOT NULL, fk_cook_id INTEGER REFERENCES cook(cook_id) NOT NULL);""")
    except psycopg2.Error as e:
        print(f"ERROR unable to create tables: {e.pgerror}")
    finally:
        cursor.close()


def on_message(ch, method, properties, body):
    # print(f"Сообщение - {body}; получено с канала - {method.routing_key}")
    logging.warning(f"Message - {json.loads(body)} by channel {method.routing_key}")


if __name__ == "__main__":
    # print("Start app....")
    logging.warning("Starting up...")

    def signal_handler(sig, frame):
        logging.info("Shutdown...")
        channel.close()
        con_pika.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    connect_to_database()
    connect_to_rabbitmq()

    channel = con_pika.channel()

    channel.queue_declare(queues[0])
    channel.queue_declare(queues[1])
    channel.queue_declare(queues[2])

    channel.basic_consume(queue=queues[0], on_message_callback=on_message, auto_ack=True)
    channel.basic_consume(queue=queues[1], on_message_callback=on_message, auto_ack=True)
    channel.basic_consume(queue=queues[2], on_message_callback=on_message, auto_ack=True)

    # create_tables()
    channel.start_consuming()
