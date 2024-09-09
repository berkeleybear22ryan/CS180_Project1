# this is to test the shifts and make sure that they all look good

from z2_ryan import load_and_split_image, trim_borders, sobel_filter
from z3_ryan import roll_with_padding, apply_shifts
import numpy as np
import matplotlib.pyplot as plt

def save_image(image, output_path):
    image_normalized = image.astype(np.float32) / np.max(image)

    fig, ax = plt.subplots(figsize=(image.shape[1] / 100, image.shape[0] / 100), dpi=100)
    ax.imshow(image_normalized)
    ax.axis('off')
    ax.set(xticks=[], yticks=[])
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    dpi = max(image.shape[0], image.shape[1]) / max(fig.get_size_inches())
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()


if __name__ == '__main__':
    image_path = "./data_tif/sculpture.tif"
    output_path = './render/TEST_ALPHA.tif'

    blue, green, red = load_and_split_image(image_path)

    print(blue.shape)
    print(green.shape)
    print(red.shape)

    top = bottom = left = right = 100
    blue = trim_borders(blue, top, bottom, left, right)
    green = trim_borders(green, top, bottom, left, right)
    red = trim_borders(red, top, bottom, left, right)

    green_offset = (33, -11)  # (y, x)
    red_offset = (140, -27)  # (y, x)

    blue, green, red = apply_shifts(blue, green, red, green_offset, red_offset)

    print(blue.shape)
    print(green.shape)
    print(red.shape)

    print("checkpoint1")

    # rgb_image = np.stack((red, green, blue), axis=-1)
    rgb_image = np.stack((sobel_filter(blue), sobel_filter(green), sobel_filter(red)), axis=-1)

    save_image(rgb_image, output_path)