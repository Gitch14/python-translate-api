import psycopg2
import time
import os
import logging
import sys
from dotenv import load_dotenv
load_dotenv()


def connect_to_db():
    for attempt in range(int(os.getenv("DB_CONNECTION_ATTEMPTS_COUNT"))):
        try:
            connection = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            logging.warning("Successfully connected to the database")
            return connection
        except Exception as e:
            print(e)
            logging.warning("I can`t connect to the database!!!")
            logging.warning(f"I wait {os.getenv("DB_CONNECTION_TIMEOUT")} seconds and connect again...")
            time.sleep(int(os.getenv("DB_CONNECTION_TIMEOUT")))
        if attempt == int(os.getenv("DB_CONNECTION_ATTEMPTS_COUNT")) - 1:
            logging.warning("Shutdown...")
            sys.exit(1)


def create_recipe(connection, title, description, type, image_path, video_path, optional, date_publish,
                  time_to_cook_and_preparing, time_to_cook, time_to_preparing, difficulty_id, calories, proteins,
                  carbohydrates, fats, author_id):
    cursor = connection.cursor()
    sql = """INSERT INTO recipe (title, description, type, image_path, video_path, optional, date_publish, 
        time_to_cook_and_preparing, time_to_cook, time_to_preparing, difficulty_id, likes, dislikes, reports, rating, 
        calories, proteins, carbohydrates, fats, author_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0,
        0.0, %s, %s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (title, description, type, image_path, video_path, optional, date_publish,
                            time_to_cook_and_preparing, time_to_cook, time_to_preparing, difficulty_id, calories,
                             proteins, carbohydrates, fats, author_id))
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()


def create_step(connection, recipe_id, step_number, step_name, image_step, text):
    cursor = connection.cursor()
    sql = """INSERT INTO recipe_step (recipe_id, step_number, step_name, image_path, text) 
        VALUES (%s, %s, %s, %s, %s)"""
    try:
        cursor.execute(sql, (recipe_id, step_number, step_name, image_step, text))
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()


def create_user(connection, email, name, password):
    cursor = connection.cursor()

    query = """SELECT EXISTS (SELECT 1 FROM usr WHERE email = %s)"""
    cursor.execute(query, (email,))
    exists = cursor.fetchone()[0]
    if exists:
        return "User already exists"
    try:
        sql = """INSERT INTO usr (email, name, password) VALUES (%s, %s, %s)"""
        cursor.execute(sql, (email, name, password))
        connection.commit()
    except Exception as e:
        print(e)
        connection.rollback()
    finally:
        cursor.close()


def delete_user(connection, email=None, id=None):
    cursor = connection.cursor()
    try:
        if email is not None:
            cursor.execute("""SELECT EXISTS (SELECT 1 FROM usr WHERE email = %s)""", (email, ))
            exists = cursor.fetchone()[0]
            if exists:
                cursor.execute("""DELETE FROM usr WHERE email = %s""", (email, ))
                connection.commit()
            else:
                return "User does not exist"
        elif id is not None:
            cursor.execute("""SELECT EXISTS (SELECT 1 FROM usr WHERE id = %s)""", (id,))
            exists = cursor.fetchone()[0]
            if exists:
                cursor.execute("""DELETE FROM usr WHERE email = %s""", (id,))
                connection.commit()
            else:
                return "User does not exist"
    except Exception as e:
        logging.warning(e)
        connection.rollback()
        return False
    finally:
        cursor.close()
    return True


if __name__ == "__main__":
    connection = connect_to_db()
    # create_recipe(connection, "Торт с яблоками", "Простой и вкусный торт с яблоками", "Десерт",
    #               "apple_cake.jpg", "apple_cake.mp4", None, "2024-02-27",
    #               "1 час 30 минут", "40 минут", "50 минут", None,
    #               300, 5, 40, 10, None)
    # create_step(connection, None, 1, "Step 1", "apple_juice.mp4",
    #             "apple juice")
    cursor = connection.cursor()
    # print(f"Result delete user  - {delete_user(connection, "test2@example.com")}")
    cursor.execute("""SELECT * FROM recipe""")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.execute("""SELECT * FROM recipe_step""")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    connection.close()
    