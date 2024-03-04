import base64
import json


def base64_to_image(base64_string: str) -> bytes:
    return base64.b64decode(base64_string)


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')


def clear_base64_string(image_base64: str) -> tuple[str, str]:
    start_index = image_base64.find("base64,") + len("base64,")
    form = image_base64.find("png")
    if form != -1:
        return image_base64[start_index:], ".png"


def save_image(image_bytes: bytes, filename: str) -> bool:
    try:
        with open(filename, 'wb') as image_file:
            image_file.write(image_bytes)
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == '__main__':
    with open("../test/create_recipe.json") as file:
        data = json.load(file)
    print(clear_base64_string(data["steps"][0]["imagePath"]))

    clear_base64, form = clear_base64_string(data["steps"][0]["imagePath"])
    file_name = "test/picture" + form

    with open(file_name, "wb") as image_file:
        image_file.write(base64_to_image(clear_base64))


