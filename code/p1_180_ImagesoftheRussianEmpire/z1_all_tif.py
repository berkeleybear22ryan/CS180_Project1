from PIL import Image
import numpy as np
import os
from skimage import io

def convert_to_16bit_tiff(source_path, target_path):
    with Image.open(source_path) as img:
        img_array = np.array(img)
        if img_array.dtype == np.uint16:
            img_16bit = img
        else:
            img_16bit = Image.fromarray((img_array * 257).astype(np.uint16))
        img_16bit.save(target_path, format='TIFF', compression='tiff_lzw')


def convert_images(source_directory, target_directory):
    images = [
        'cathedral.jpg', 'church.tif', 'emir.tif', 'harvesters.tif',
        'icon.tif', 'lady.tif', 'melons.tif', 'monastery.jpg',
        'onion_church.tif', 'sculpture.tif', 'self_portrait.tif',
        'three_generations.tif', 'tobolsk.jpg', 'train.tif'
    ]

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for image_name in images:
        source_path = os.path.join(source_directory, image_name)
        target_name = os.path.splitext(image_name)[0] + '.tif'
        target_path = os.path.join(target_directory, target_name)
        convert_to_16bit_tiff(source_path, target_path)
        print(f"Converted {image_name} to 16-bit TIFF and saved to {target_directory}.")


# 8-bit: 0 to 255 ...2^8
# 16-bit: 0 to 65535 ...2^16
if __name__ == '__main__':
    source_directory = './data/'
    target_directory = './data_tif/'
    convert_images(source_directory, target_directory)

    for filename in os.listdir("./data_tif"):
        img = io.imread("./data_tif/" + filename)
        print(filename + ": " + str(img.dtype))