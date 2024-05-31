import os
import cv2
import matplotlib.pyplot as plt
import random
import time
import concurrent.futures
import json
import jpeglib
import lsb 
import jsteg


def get_payloads_js():
    path = 'payloads/javascript-malware-collection'
    years = ['1936', '2015', '2016', '2017', '2019']
    payload_paths = [os.path.join(path, year, dir, file) 
                     for year in years 
                     for dir in os.listdir(os.path.join(path, year)) 
                     for file in os.listdir(os.path.join(path, year, dir))]

    payloads = [open(p, 'r').read() for p in payload_paths if os.path.getsize(p) * 10 < 512 * 512 * 3]
    random.shuffle(payloads)
    return payloads[:12000]


def get_payloads_url():
    # http://gjhfhgdg.insane.wang/dll/dffgfgfgfd.jpeg 

    with open('payloads/urlhaus_full.json', 'r') as f:
        payloads_json = json.load(f)

    payloads = [item['url'] 
                for payload in payloads_json
                for item in payloads_json[payload]]
    
    random.shuffle(payloads)
    return payloads[:12000]


def embed_payload_lsb(image_path, payload, output):
    try:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        stego_img = lsb.embed_message(img, payload)

        stego_img = cv2.cvtColor(stego_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output, stego_img)
    except Exception as e:
        print(f'An error occured: {e.message}')


def embed_payload_jsteg(image_path, payload, output):
    img = jpeglib.read_dct(image_path)
    stego_img = jsteg.embed_message(img, payload)
    if stego_img is not None:
        stego_img.write_dct(output)
    else:
        print("aici")
        with open('payloads/javascript-malware-collection/2016/20160908/20160908_f692000612b59b6dc5e4e5510dfae151.js', 'r') as f:
            small_payload = f.read()

            stego_img = jsteg.embed_message(img, small_payload)
            if stego_img is not None:
                stego_img.write_dct(output)
            else:
                print("Si asta a fost prea mare")


def process_images(images, payloads, ptype, split, alg):
    inc = 0
    if split == 'val':
        inc = 8000
    elif split == 'test':
        inc = 10000

    with concurrent.futures.ProcessPoolExecutor() as executor:
        if alg == 'lsb':
            results = [executor.submit(embed_payload_lsb, images[i], payloads[i], f'datasets/stego_dataset/{split}/stego/{alg}/{ptype}/{i + inc}_{ptype}.png') for i in range(len(images))]
        elif alg == 'jsteg':
            results = [executor.submit(embed_payload_jsteg, images[i], payloads[i], f'datasets/stego_dataset/{split}/stego/{alg}/{ptype}/{i + inc}_{ptype}.jpg') for i in range(len(images))]   
        concurrent.futures.wait(results)


def main():
    ptype = 'url'
    alg = 'jsteg'

    if ptype == 'js':
        payloads = get_payloads_js()
    elif ptype == 'url':
        payloads = get_payloads_url()
    
    train_payloads, val_payloads, test_payloads = payloads[:8000], payloads[8000:10000], payloads[10000:]

    if alg == 'lsb':
        train_images = [f'datasets/stego_dataset/train/clean/png/{i}.png' for i in range(8000)]
        val_images = [f'datasets/stego_dataset/val/clean/png/{i}.png' for i in range(8000, 10000)]
        test_images = [f'datasets/stego_dataset/test/clean/png/{i}.png' for i in range(10000, 12000)]
    elif alg == 'jsteg':
        train_images = [f'datasets/stego_dataset/train/clean/jpeg/{i}.jpg' for i in range(8000)]
        val_images = [f'datasets/stego_dataset/val/clean/jpeg/{i}.jpg' for i in range(8000, 10000)]
        test_images = [f'datasets/stego_dataset/test/clean/jpeg/{i}.jpg' for i in range(10000, 12000)]

    print(len(train_images), len(train_images))
    print(len(val_payloads), len(val_images))
    print(len(test_payloads), len(test_images))

    t1 = time.perf_counter()
    process_images(train_images, train_payloads, ptype, 'train', alg)
    process_images(val_images, val_payloads, ptype, 'val', alg)
    process_images(test_images, test_payloads, ptype, 'test', alg)
    t2 = time.perf_counter()

    print(f'Time to process images: {(t2 - t1):.2f}')


if __name__ == "__main__":
    main()


# Fara multiprocessing pentru 100 imagini: 10.86 sec (cu functia mea de lsb embedding)
# Cu multiprocessing pt 100 imagini: 3.95 sec
# Cu multithreading: 8.94 sec
    
# Toate imaginile cu playload-uri js: 654.67 sec = 10.91 min
# Toate imaginile cu playload-uri url: 29.42 sec
    

# Functia mea de jsteg pentru 100 de imagini cu multiprocessing: 1.22 sec
# Toate imaginile cu payload-urile js: 1286.36 sec = 21.43 min
# Toate imaginile cu payload-urile url: 26.35 sec