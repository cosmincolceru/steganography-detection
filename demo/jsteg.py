import jpeglib
import numpy as np
import argparse
import os

byte_size = 8
size_encoding = 4  # number of bytes taken by the size of the message

def embed_message(image: jpeglib.dct_jpeg, message: str) -> jpeglib.dct_jpeg:
    """Embed a message into the DCT coefficients of a JPEG iamage"""
    
    message_bits = ''.join(f'{ord(char):08b}' for char in message)   # Conver the message to a string of bits
    message_bits = f'{len(message_bits):032b}' + message_bits        # Prepend length of message in bits

    Y = image.Y
    Cr = image.Cr
    Cb = image.Cb
    
    all_coeffs = np.concatenate((Y.flatten(), Cr.flatten(), Cb.flatten()))

    try:
        j = 0
        for i in range(len(message_bits)):
            while all_coeffs[j] == 0 or all_coeffs[j] == 1:     # Skip the DCT coefficients that are 0 or 1
                j += 1
            
            all_coeffs[j] = (all_coeffs[j] & ~1) | int(message_bits[i]) 
            j += 1
    
        image.Y = all_coeffs[:Y.size].reshape(Y.shape)
        image.Cr = all_coeffs[Y.size:Y.size + Cr.size].reshape(Cr.shape)
        image.Cb = all_coeffs[Y.size + Cr.size:].reshape(Cb.shape)

        return image

    except Exception as e:
        print("The message is too long for the cover image")
        return None


def extract_message(image: jpeglib.dct_jpeg) -> str:
    """Extract the message textract_messagehat has been embeded into the DCT coefficients of a JPEG image"""

    Y = image.Y
    Cr = image.Cr
    Cb = image.Cb
    
    all_coeffs = np.concatenate((Y.flatten(), Cr.flatten(), Cb.flatten()))  # Create an array with all the DCT coefficients

    size_coeff = []     # Extract the coefficients that encode the size of the message
    j = 0
    for _ in range(byte_size * size_encoding):
        while all_coeffs[j] == 0 or all_coeffs[j] == 1:     # Skip the DCT coefficients that are 0 or 1
            j += 1
        
        size_coeff.append(all_coeffs[j])
        j += 1

    size_bin = ''.join(str(i & 1) for i in size_coeff)     # Decode the size
    size = int(size_bin, 2)

    message_coeff = []     # Extract the coefficients that encode the message
    for _ in range(size):
        while all_coeffs[j] == 0 or all_coeffs[j] == 1:     # Skip the DCT coefficients that are 0 or 1
            j += 1
        
        message_coeff.append(all_coeffs[j])
        j += 1

    message_bin = ''.join(str(i & 1) for i in (message_coeff))                                      # Convert the coefficients to a string of 1s and 0s
    chars_bin = [message_bin[i:i + byte_size] for i in range(0, len(message_bin), byte_size)]       # Split the string into substrings, each corresponding to a character
    message = ''.join([chr(int(char_bin, 2)) for char_bin in chars_bin])                            # Decode each character to form the message

    return message


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["embed", "extract"], help="Specify encode or decode") 
    parser.add_argument("--image", "-i", help="Path to the input image")
    parser.add_argument("--message", "-m", help="Path to a text file containing the message. Not used if the mode is decode")
    parser.add_argument("--output", "-o", help="Path to the output image. Not used if the mode is decode", default="stego_img.jpg")

    args = parser.parse_args()
   
    image_path = args.image
    _, extension = os.path.splitext(image_path)
    assert extension.lower() == ".jpg" or extension.lower() == ".jpeg" 
    
    image = jpeglib.read_dct(image_path)

    if args.mode == "embed":
        message_path = args.message
        output_name = args.output
        _, extension = os.path.splitext(output_name)
        assert extension.lower() == ".jpg" or extension.lower() == ".jpeg" 

        with open(message_path) as f:
            message = f.read()
        
        new_image = embed_message(image, message)
        if new_image is not None:
            new_image.write_dct(output_name)
    
    else:
        message = extract_message(image) 
        print(message)


if __name__ == "__main__":
    main()

