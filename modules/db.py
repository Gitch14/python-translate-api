import psycopg2
import time
import os
import logging
import sys
from modules.image import base64_to_image
from modules.s3 import put_file, check_exist, delete_file
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


def create_recipe(connection, s3_client, recipe: dict):
    cursor = connection.cursor()
    cursor.execute("""SELECT MAX(id) FROM recipe""")
    res_max_id = cursor.fetchone()
    if res_max_id[0] is not None:
        recipe["recipe_id"] = res_max_id[0] + 1
    else:
        # print(f"Строка 40 --> {cursor.fetchone()}")
        recipe["recipe_id"] = 1
    recipe_sql = """INSERT INTO recipe (id, title, description, type, image_path, video_path, optional, date_publish, 
        time_to_cook_and_preparing, time_to_cook, time_to_preparing, difficulty_id, likes, dislikes, reports, rating, 
        calories, proteins, carbohydrates, fats, author_id) VALUES (%(recipe_id)s, %(title)s, %(description)s, %(type)s,
         %(image)s, %(video)s, %(optional)s, %(datePublish)s, %(timeToCookAndPreparing)s, %(timeToCook)s, 
        %(timeToPreparing)s, %(difficulty)s, 0, 0, 0, 0.0, null, null, null, null, %(userId)s)"""
    # cursor.execute("""SELECT MAX(id) FROM recipe_step""")
    # step_id = cursor.fetchone()[0] + 1
    step_sql = """INSERT INTO recipe_step (id, recipe_id, step_number, step_name, image_path, text) 
        VALUES (%(step_id)s, %(recipe_id)s, %(stepNumber)s, %(stepName)s, %(image_path)s, %(text)s)"""
    ingredients_sql = """INSERT INTO ingredient (id, recipe_id, name, value) 
        VALUES (%(id)s, %(recipe_id)s, %(name)s, %(value)s)"""
    try:
        print(recipe)
        cursor.execute(recipe_sql, recipe)
        for step in recipe["steps"]:
            cursor.execute("""SELECT MAX(id) FROM recipe_step""")
            res_max_id = cursor.fetchone()
            if res_max_id[0] is not None:
                step["step_id"] = res_max_id[0] + 1
            else:
                step["step_id"] = 1
            step["recipe_id"] = recipe["recipe_id"]
            if step["image"]["type"] == "image":
                image_data = base64_to_image(step["image"]["data"])
                step["image_path"] = (f"/user-{recipe["userId"]}/recipe-{recipe["recipe_id"]}"
                                      f"/{step["stepName"] + "." + step["image"]["format"]}")
                put_file_res = put_file(s3_client, os.getenv('S3_BUCKET_NAME'), step["image_path"], image_data)
                if not put_file_res and not check_exist(s3_client, os.getenv('S3_BUCKET_NAME'), step["image_path"]):
                    if not put_file(s3_client, os.getenv('S3_BUCKET_NAME'), step["image_path"], image_data):
                        raise Exception("Upload Failed")
                cursor.execute(step_sql, step)

        for ingredient in recipe["ingredients"]:
            cursor.execute("""SELECT MAX(id) FROM ingredient""")
            res_max_id = cursor.fetchone()
            if res_max_id[0] is not None:
                ingredient["id"] = res_max_id[0] + 1
            else:
                ingredient["id"] = 1
            ingredient["recipe_id"] = recipe["recipe_id"]
            cursor.execute(ingredients_sql, ingredient)

        connection.commit()
        return True
    except Exception as e:
        print(f"Это 77 {e}")
        connection.rollback()
        for step in recipe["steps"]:
            if "image_path" in step and check_exist(s3_client, os.getenv('S3_BUCKET_NAME'), step["image_path"]):
                delete_file(s3_client, os.getenv('S3_BUCKET_NAME'), step["image_path"])
        return False
    finally:
        cursor.close()


def create_user(connection, user: dict):
    cursor = connection.cursor()
    print("Создание пользователя")
    cursor.execute("""SELECT EXISTS (SELECT 1 FROM usr WHERE email = %(email)s)""", user)
    exists = cursor.fetchone()[0]
    if exists:
        return "User already exists"
    try:
        cursor.execute("""INSERT INTO usr (email, name, password) VALUES (%(email)s, %(name)s, %(password)s)""", user)
        connection.commit()
        return True
    except Exception as e:
        print(e)
        connection.rollback()
        return False
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

    # cursor.execute("""SELECT * FROM recipe""")
    # for row in cursor.fetchall():
    #     print(row)

    cursor.execute("""SELECT * FROM ingredient""")
    # print(type(cursor.fetchone()[0]))
    result = cursor.fetchall()
    for row in result:
        print(row)

    # if result[0] is None:
    #     print("Это тип None")
    # elif type(result[0]) == int:
    #     print(f"Нет, это число -> {result[0]}")
    connection.close()
    