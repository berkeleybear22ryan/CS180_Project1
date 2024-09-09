# cleared up frame one ... this should be better but kept other as that is what I used and did not want to rerender it all
# so just can use this on sculpture.tif and z6_ryan.py on othere

import os
import numpy as np
from skimage import io
from z2_ryan import load_and_split_image, sobel_filter
from z3_ryan import apply_shifts
import matplotlib.pyplot as plt
import multiprocessing


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_image(image, output_path):
    image_float = image.astype(np.float32) / np.max(image)
    plt.imsave(output_path, image_float)


def process_image(args):
    idx, image_name, shifts, total_images = args
    print(f"Processing image {idx}/{total_images}: {image_name}")

    input_path = f'./data_tif/{image_name}'
    output_folder = f'./frames/{idx}'
    ensure_dir(f'{output_folder}/normal')
    ensure_dir(f'{output_folder}/sobel')

    blue, green, red = load_and_split_image(input_path)
    green_offset, red_offset = shifts[image_name]

    frame_count = 0

    current_green_offset = [0, 0]
    while current_green_offset != list(green_offset):
        if current_green_offset[0] != green_offset[0]:
            current_green_offset[0] += 1 if green_offset[0] > 0 else -1
        elif current_green_offset[1] != green_offset[1]:
            current_green_offset[1] += 1 if green_offset[1] > 0 else -1

        shifted_green, _ = apply_shifts(blue, green, red, tuple(current_green_offset), (0, 0))[1:]
        normal_image = np.stack((red, shifted_green, blue), axis=-1)
        sobel_image = np.stack((sobel_filter(red), sobel_filter(shifted_green), sobel_filter(blue)), axis=-1)

        save_image(normal_image, f'{output_folder}/normal/{frame_count:012d}.jpeg')
        save_image(sobel_image, f'{output_folder}/sobel/{frame_count:012d}.jpeg')
        frame_count += 1

    final_shifted_green, _ = apply_shifts(blue, green, red, green_offset, (0, 0))[1:]
    current_red_offset = [0, 0]
    while current_red_offset != list(red_offset):
        if current_red_offset[0] != red_offset[0]:
            current_red_offset[0] += 1 if red_offset[0] > 0 else -1
        elif current_red_offset[1] != red_offset[1]:
            current_red_offset[1] += 1 if red_offset[1] > 0 else -1

        _, shifted_red = apply_shifts(blue, green, red, green_offset, tuple(current_red_offset))[1:]
        normal_image = np.stack((shifted_red, final_shifted_green, blue), axis=-1)
        sobel_image = np.stack((sobel_filter(shifted_red), sobel_filter(final_shifted_green), sobel_filter(blue)),
                               axis=-1)

        save_image(normal_image, f'{output_folder}/normal/{frame_count:012d}.jpeg')
        save_image(sobel_image, f'{output_folder}/sobel/{frame_count:012d}.jpeg')
        frame_count += 1

    print(f"Processed {frame_count} frames for {image_name}")


if __name__ == '__main__':
    # images = [
    #     'cathedral.tif', 'church.tif', 'emir.tif', 'harvesters.tif',
    #     'icon.tif', 'lady.tif', 'melons.tif', 'monastery.tif',
    #     'onion_church.tif', 'sculpture.tif', 'self_portrait.tif',
    #     'three_generations.tif', 'tobolsk.tif', 'train.tif'
    # ]
    images = ['sculpture.tif']

    shifts = {
        # 'cathedral.tif': ((5, 2), (12, 3)),
        # 'church.tif': ((25, 4), (58, -4)),
        # 'emir.tif': ((49, 24), (107, 41)),
        # 'harvesters.tif': ((60, 18), (123, 14)),
        # 'icon.tif': ((41, 18), (90, 23)),
        # 'lady.tif': ((53, 8), (114, 14)),
        # 'melons.tif': ((82, 10), (182, 13)),
        # 'monastery.tif': ((-3, 2), (3, 2)),
        # 'onion_church.tif': ((51, 27), (109, 37)),
        'sculpture.tif': ((33, -11), (140, -27)),
        # 'self_portrait.tif': ((78, 29), (175, 37)),
        # 'three_generations.tif': ((52, 13), (111, 11)),
        # 'tobolsk.tif': ((3, 3), (7, 3)),
        # 'train.tif': ((43, 8), (86, 33)),
    }

    total_images = len(images)
    args = [(idx + 1, image, shifts, total_images) for idx, image in enumerate(images)]

    num_cores = min(multiprocessing.cpu_count(), 14)

    with multiprocessing.Pool(num_cores) as pool:
        pool.map(process_image, args)

    print("All images processed.")