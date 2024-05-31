import argparse
import cv2
import os
import numpy as np

byte_size = 8
size_encoding = 4  # number of bytes taken by the size of the message

class StegoExeption(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def embed_message(image: np.ndarray, message: str) -> np.ndarray:
    """Embed a message into the LSBs of the pixels of an image"""
    
    max_message_length = image.size // byte_size - byte_size * size_encoding
    if len(message)> max_message_length:
        raise StegoExeption(f'Message too long. Maximum length of the message that can be encoded in this image is {max_message_length} characters.')

    message_bits = ''.join(f'{ord(char):08b}' for char in message)  # Conver the message to a string of bits
    message_bits = f'{len(message_bits):032b}' + message_bits       # Prepend length of message in bits

    image_flat = image.flatten()

    for i in range(len(message_bits)):
        image_flat[i] = (image_flat[i] & ~1) | int(message_bits[i])     # Change the lsb to the corresponding message bit

    new_image = image_flat.reshape(image.shape)
    return new_image


def extract_message(image: np.ndarray) -> str:
    """Extract the message embeded into the LSBs of the pixels of an image"""
    
    image_flat = image.flatten()

    size_pixels = image_flat[:byte_size * size_encoding]  # Extract the pixels where the size of the message is encoded and decode them
    size_bin = ''.join(str(i & 1) for i in size_pixels)
    size = int(size_bin, 2)

    message_pixels = image_flat[byte_size * size_encoding:byte_size * size_encoding + size]         # Extract the pixels where the message is stored
    message_bin = ''.join(str(i & 1) for i in (message_pixels))                                     # Convert the pixels to a string of 1s and 0s
    chars_bin = [message_bin[i:i + byte_size] for i in range(0, len(message_bin), byte_size)]       # Split the string into substrings, each corresponding to a character
    message = ''.join([chr(int(char_bin, 2)) for char_bin in chars_bin])                            # Decode each character to form the message

    return message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["embed", "extract"], help="Specify encode or decode") 
    parser.add_argument("--image", "-i", help="Path to the input image")
    parser.add_argument("--message", "-m", help="Path to a text file containing the message. Not used if the mode is decode")
    parser.add_argument("--output", "-o", help="Path to the output image. Not used if the mode is decode", default="stego_img.png")

    args = parser.parse_args()
   
    image_path = args.image
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    if args.mode == "embed":
        message_path = args.message
        output_name = args.output
        _, extension = os.path.splitext(output_name)
        assert extension.lower() == ".png"

        with open(message_path) as f:
            message = f.read()
        
        new_image = embed_message(image, message)
        if new_image is not None:
            cv2.imwrite(output_name, new_image)
    
    else:
        _, extension = os.path.splitext(image_path)
        assert extension.lower() == ".png" 

        message = extract_message(image) 
        print(message)


if __name__ == "__main__":
    main()

