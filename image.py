import base64


def base64_to_image(base64_string: str) -> bytes:
    return base64.b64decode(base64_string)


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode('utf-8')


def save_image(image_bytes: bytes, filename: str) -> bool:
    try:
        with open(filename, 'wb') as image_file:
            image_file.write(image_bytes)
        return True
    except Exception as e:
        print(e)
        return False
