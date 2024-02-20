import pika
import psycopg2
import json
import sys
import signal


queues = ["create", "update", "remove", "status"]
con_db = None


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
    print(f"Сообщение - {body}; получено с канала - {method.routing_key}")


if __name__ == "__main__":
    con_db = psycopg2.connect(
        dbname="manga_translation_db",
        user="admin",
        password="admin1234",
        host="localhost",
        port="6544"
    )

    con_pika = pika.BlockingConnection(pika.ConnectionParameters("localhost", 5672, "/", pika.PlainCredentials("user", "111")))
    channel = con_pika.channel()

    channel.queue_declare(queues[0])
    channel.queue_declare(queues[1])
    channel.queue_declare(queues[2])

    channel.basic_consume(queue=queues[0], on_message_callback=on_message, auto_ack=True)
    channel.basic_consume(queue=queues[1], on_message_callback=on_message, auto_ack=True)
    channel.basic_consume(queue=queues[2], on_message_callback=on_message, auto_ack=True)

    create_tables()


    def signal_handler(sig, frame):
        print("Завершение работы...")
        channel.close()
        con_pika.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    channel.start_consuming()
