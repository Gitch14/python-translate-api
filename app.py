from modules.rabbitmq import connect_to_rabbitmq, declare_and_consume_queues
from modules.rabbitmq import queues
from modules.db import connect_to_db
from modules.s3 import s3_connect
import logging


def main():
    logging.warning('Starting app...')
    s3_connection = s3_connect()
    connection_db = connect_to_db()
    connection_pika = connect_to_rabbitmq(connection_db, s3_connection)
    channel = declare_and_consume_queues(connection_pika, queues)

    channel.start_consuming()


if __name__ == "__main__":
    main()
