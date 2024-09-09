import os
import numpy as np
from skimage import io
from z2_ryan import load_and_split_image, sobel_filter
from z3_ryan import apply_shifts
import matplotlib.pyplot as plt


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def save_image(image, output_path):
    image_float = image.astype(np.float32) / np.max(image)
    plt.imsave(output_path, image_float)


def process_images(images, shifts):
    for idx, image_name in enumerate(images, 1):
        print(f"Processing image {idx}/{len(images)}: {image_name}")

        input_path = f'./data_tif/{image_name}'
        output_folder = f'./frames/{idx}'
        ensure_dir(f'{output_folder}/normal')
        ensure_dir(f'{output_folder}/sobel')

        blue, green, red = load_and_split_image(input_path)
        green_offset, red_offset = shifts[image_name]

        height, width = blue.shape
        frame_count = 0

        # start positions at -3/4 of resolution -- so that the frames are less
        start_y, start_x = int(-0.75 * height), int(-0.75 * width)

        for y in range(start_y, green_offset[0] + 1):
            shifted_green = apply_shifts(blue, green, red, (y, start_x), (start_y, start_x))[1]
            shifted_red = apply_shifts(blue, green, red, (y, start_x), (start_y, start_x))[2]

            normal_image = np.stack((shifted_red, shifted_green, blue), axis=-1)
            sobel_image = np.stack((sobel_filter(shifted_red), sobel_filter(shifted_green), sobel_filter(blue)),
                                   axis=-1)

            save_image(normal_image, f'{output_folder}/normal/{frame_count:012d}.png')
            save_image(sobel_image, f'{output_folder}/sobel/{frame_count:012d}.png')
            frame_count += 1

        for x in range(start_x, green_offset[1] + 1):
            shifted_green = apply_shifts(blue, green, red, (green_offset[0], x), (start_y, start_x))[1]
            shifted_red = apply_shifts(blue, green, red, (green_offset[0], x), (start_y, start_x))[2]

            normal_image = np.stack((shifted_red, shifted_green, blue), axis=-1)
            sobel_image = np.stack((sobel_filter(shifted_red), sobel_filter(shifted_green), sobel_filter(blue)),
                                   axis=-1)

            save_image(normal_image, f'{output_folder}/normal/{frame_count:012d}.png')
            save_image(sobel_image, f'{output_folder}/sobel/{frame_count:012d}.png')
            frame_count += 1






        for y in range(start_y, red_offset[0] + 1):
            shifted_green = apply_shifts(blue, green, red, green_offset, (y, start_x))[1]
            shifted_red = apply_shifts(blue, green, red, green_offset, (y, start_x))[2]

            normal_image = np.stack((shifted_red, shifted_green, blue), axis=-1)
            sobel_image = np.stack((sobel_filter(shifted_red), sobel_filter(shifted_green), sobel_filter(blue)),
                                   axis=-1)

            save_image(normal_image, f'{output_folder}/normal/{frame_count:012d}.png')
            save_image(sobel_image, f'{output_folder}/sobel/{frame_count:012d}.png')
            frame_count += 1



        for x in range(start_x, red_offset[1] + 1):
            shifted_green = apply_shifts(blue, green, red, green_offset, (red_offset[0], x))[1]
            shifted_red = apply_shifts(blue, green, red, green_offset, (red_offset[0], x))[2]

            normal_image = np.stack((shifted_red, shifted_green, blue), axis=-1)
            sobel_image = np.stack((sobel_filter(shifted_red), sobel_filter(shifted_green), sobel_filter(blue)),
                                   axis=-1)

            save_image(normal_image, f'{output_folder}/normal/{frame_count:012d}.png')
            save_image(sobel_image, f'{output_folder}/sobel/{frame_count:012d}.png')
            frame_count += 1


if __name__ == '__main__':
    images = [
        'cathedral.tif', 'church.tif', 'emir.tif', 'harvesters.tif',
        'icon.tif', 'lady.tif', 'melons.tif', 'monastery.tif',
        'onion_church.tif', 'sculpture.tif', 'self_portrait.tif',
        'three_generations.tif', 'tobolsk.tif', 'train.tif'
    ]

    shifts = {
        'cathedral.tif': ((5, 2), (12, 3)),
        'church.tif': ((25, 4), (58, -4)),
        'emir.tif': ((49, 24), (107, 41)),
        'harvesters.tif': ((60, 18), (123, 14)),
        'icon.tif': ((41, 18), (90, 23)),
        'lady.tif': ((53, 8), (114, 14)),
        'melons.tif': ((82, 10), (182, 13)),
        'monastery.tif': ((-3, 2), (3, 2)),
        'onion_church.tif': ((51, 27), (109, 37)),
        'sculpture.tif': ((33, -11), (140, -27)),
        'self_portrait.tif': ((78, 29), (175, 37)),
        'three_generations.tif': ((52, 13), (111, 11)),
        'tobolsk.tif': ((3, 3), (7, 3)),
        'train.tif': ((43, 8), (86, 33)),
    }

    process_images(images, shifts)