import argparse
import requests

url = "http://localhost:5000/predict"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to the input image")
    args = parser.parse_args()
    image_path = args.image

    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
        
    prediction = response.json()['prediction'][0][0]
    
    # print(prediction)
    if prediction > 0.5:
        print('STEGO')
    else:
        print('CLEAN')

if __name__ == '__main__':
    main()