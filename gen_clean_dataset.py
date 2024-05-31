import os
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import time
import random
import concurrent.futures


def get_images_animals():
    path = 'datasets/for_custom/animals/animals/animals'
    images = [os.path.join(path, animal, image)
              for animal in os.listdir(path)
              for image in os.listdir(os.path.join(path, animal))]
    
    random.shuffle(images)
    return images[:-541]


def get_images_people():
    path = 'datasets/for_custom/people/images/images'
    images = [os.path.join(path, image) 
              for image in os.listdir(path)]
    random.shuffle(images)
    return images


def get_images_people_2():
    path = 'datasets/for_custom/people_2/images'
    images = [os.path.join(path, image) 
              for image in os.listdir(path)]
    random.shuffle(images)
    return images


def get_images_objects():
    path = 'datasets/for_custom/objects'
    images = [os.path.join(path, dir, 'images', image)
              for dir in os.listdir(path)
              for image in os.listdir(os.path.join(path, dir, 'images'))]
    random.shuffle(images)
    return images


def get_images_cars():
    path = 'datasets/for_custom/cars'
    dirs = ['train', 'valid', 'test']
    images = [os.path.join(path, dir, 'images', image)
              for dir in dirs
              for image in os.listdir(os.path.join(path, dir, 'images'))]
    random.shuffle(images)
    return images


def get_images_buildings():
    path = 'datasets/for_custom/buildings'
    images = [os.path.join(path, image) for image in os.listdir(path)]
    random.shuffle(images)
    return images


def get_all_images():
    animals_images = get_images_animals()
    people_images = get_images_people()
    people_images_2 = get_images_people_2()
    objects_images = get_images_objects()
    buildings_images = get_images_buildings()
    cars_images = get_images_cars()
    
    print(f'Animals - {len(animals_images)} images')
    print(f'People - {len(people_images)} images')
    print(f'People 2 - {len(people_images_2)} images')
    print(f'Objects - {len(objects_images)} images')
    print(f'Buildings - {len(buildings_images)} images')
    print(f'Cars - {len(cars_images)} images')
    
    images = animals_images + people_images + people_images_2 + objects_images + buildings_images + cars_images
    random.shuffle(images)

    print(f'Total - {len(images)} images')

    return images

def get_dir(current_index, total_images, val_size, test_size):
    dir = 'train'
    if current_index >= (total_images - val_size - test_size) and current_index < (total_images - test_size):
        dir = 'val'
    elif current_index >= (total_images - test_size):
        dir = 'test'
    
    return dir

def process_image(image_path, index):
    try:
        image = Image.open(image_path)
        image = image.convert("RGB")
        image = image.resize((512, 512)) 

        dir = get_dir(index, 12000, 2000, 2000)
        image.save(f'datasets/custom/{dir}/clean/jpeg/{index}.jpg', format="JPEG")
        image.save(f'datasets/custom/{dir}/clean/png/{index}.png', format="PNG")
    except Exception as e:
        print(f"An error occurred while processing image {image_path}: {e}")


def main():
    images = get_all_images()

    t1 = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(process_image, image, i) for i, image in enumerate(images)]
        concurrent.futures.wait(results)

    t2 = time.perf_counter()

    print(f'Time to process {len(images)} images: {(t2 - t1):.2f}s')


if __name__ == "__main__":
    main()



# 8.6 secunde pentru 100 de poze => 0.086 secunde pe poza => 7.74 minute pentru 5400 poze fara paralelizare
# 1.20 secunde cu procese => 56s pentru tot dataset-ul cu animale (5400 poze)
# 1.74 secunde cu thread-uri
# Time to process 12000 images: 118.86s (folosing multi-processing)



# t1 = time.perf_counter()

# for i, image_path in enumerate(images[:100]):
#     process_image(image_path, i)

# t2 = time.perf_counter()

# print((t2 - t1) / 100)