import requests

url = "http://localhost:5000/predict"


# image_path = 'datasets/stego_dataset/test/clean/jpeg/10008.jpg'

for i in range(10, 100):
    image_path = f'datasets/stego_dataset/test/stego/jsteg/js/100{i}_js.jpg'
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)

    # Print the response
        
    prediction = response.json()['prediction'][0][0]
    print(prediction, end=': ')
    if prediction > 0.5:
        print('STEGO')
    else:
        print('CLEAN')
