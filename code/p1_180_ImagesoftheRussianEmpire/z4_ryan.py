import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import rescale
from skimage.io import imread
# from z2_ryan import load_and_split_image, sobel_filter, trim_borders

def euclidean_distance(img1, img2):
    return np.sqrt(np.mean((img1.astype(np.float32) - img2.astype(np.float32)) ** 2))


# shift by (y, x) pixels + filling empty space with zeros
def shift_image(image, shift):
    dy, dx = shift
    height, width = image.shape
    shifted = np.zeros_like(image)

    if dy >= 0:
        y_src, y_dst = 0, dy
        y_range = height - dy
    else:
        y_src, y_dst = -dy, 0
        y_range = height + dy

    if dx >= 0:
        x_src, x_dst = 0, dx
        x_range = width - dx
    else:
        x_src, x_dst = -dx, 0
        x_range = width + dx

    shifted[y_dst:y_dst + y_range, x_dst:x_dst + x_range] = image[y_src:y_src + y_range, x_src:x_src + x_range]
    return shifted


def align_images(fixed, moving, window):
    best_score = float('inf')
    best_offset = (0, 0)

    height, width = fixed.shape
    for dy in range(-window, window + 1):
        for dx in range(-window, window + 1):
            shifted = shift_image(moving, (dy, dx))
            score = euclidean_distance(fixed, shifted)
            if score < best_score:
                best_score = score
                best_offset = (dy, dx)

    return best_offset


def downscale_image(image):
    return rescale(image, 0.5, channel_axis=2, anti_aliasing=True, preserve_range=True).astype(image.dtype)


def process_image_pyramid(image, initial_window, num_levels):
    pyramid = [image]
    for _ in range(num_levels - 1):
        pyramid.append(downscale_image(pyramid[-1]))

    print(f"Starting pyramid alignment with {num_levels} levels")

    b, g, r = pyramid[-1][:, :, 0], pyramid[-1][:, :, 1], pyramid[-1][:, :, 2]
    window = max(initial_window // (2 ** (num_levels - 1)), 1)

    print(f"Initial alignment at lowest resolution (Level {num_levels - 1}):")
    print(f"Window size: {window}")

    g_offset = align_images(b, g, window)
    r_offset = align_images(b, r, window)

    print(f"Initial G offset: {g_offset}")
    print(f"Initial R offset: {r_offset}")

    for level in range(num_levels - 2, -1, -1):
        print(f"\nRefining alignment at Level {level}:")
        scale_factor = 2 ** (num_levels - 1 - level)
        window = max(initial_window // scale_factor, 1)

        # make sure to catch this error in case enter window is larger then dimensions
        max_window = min(b.shape) // 10
        window = min(window, max_window)

        print(f"Window size: {window}")

        b, g, r = pyramid[level][:, :, 0], pyramid[level][:, :, 1], pyramid[level][:, :, 2]

        g_offset = (g_offset[0] * 2, g_offset[1] * 2)
        r_offset = (r_offset[0] * 2, r_offset[1] * 2)

        print(f"Scaled up G offset: {g_offset}")
        print(f"Scaled up R offset: {r_offset}")

        aligned_g = shift_image(g, g_offset)
        aligned_r = shift_image(r, r_offset)

        refined_g_offset = align_images(b, aligned_g, window)
        refined_r_offset = align_images(b, aligned_r, window)
        print(f"Refinement for G: {refined_g_offset}")
        print(f"Refinement for R: {refined_r_offset}")

        g_offset = (g_offset[0] + refined_g_offset[0], g_offset[1] + refined_g_offset[1])
        r_offset = (r_offset[0] + refined_r_offset[0], r_offset[1] + refined_r_offset[1])
        print(f"Updated G offset: {g_offset}")
        print(f"Updated R offset: {r_offset}")

    print("\nFinal alignment:")
    b, g, r = image[:, :, 0], image[:, :, 1], image[:, :, 2]
    aligned_g = shift_image(g, g_offset)
    aligned_r = shift_image(r, r_offset)

    print(f"Final G channel offset: {g_offset}")
    print(f"Final R channel offset: {r_offset}")

    return np.dstack((b, aligned_g, aligned_r)), [g_offset, r_offset]


def align_channels(image, initial_window=15, num_levels=4):
    return process_image_pyramid(image, initial_window, num_levels)


# def main():
#     image_path = './data_tif/lady.tif'
#     blue, green, red = load_and_split_image(image_path)
#     print(blue.shape)
#     print(green.shape)
#     print(red.shape)
#
#     crop_amnt = int(min(blue.shape) / 3)
#     print(trim_borders(sobel_filter(blue), crop_amnt, crop_amnt, crop_amnt, crop_amnt).shape)
#     # exit(1)
#     # crop_amnt = 0
#
#     image = np.stack(
#         (trim_borders(sobel_filter(blue), crop_amnt, crop_amnt, crop_amnt, crop_amnt),
#          trim_borders(sobel_filter(green), crop_amnt, crop_amnt, crop_amnt, crop_amnt),
#          trim_borders(sobel_filter(red), crop_amnt, crop_amnt, crop_amnt, crop_amnt)), axis=-1)
#
#     # image = np.stack(
#     #     (trim_borders(blue, crop_amnt, crop_amnt, crop_amnt, crop_amnt),
#     #      trim_borders(green, crop_amnt, crop_amnt, crop_amnt, crop_amnt),
#     #      trim_borders(red, crop_amnt, crop_amnt, crop_amnt, crop_amnt)), axis=-1)
#
#     # image = np.stack((
#     #     sobel_filter(blue),
#     #     sobel_filter(green),
#     #     sobel_filter(red)), axis=-1)
#
#
#     # make sure the window is not larger than res after crop o/w will error
#     result, offsets = align_channels(image, initial_window=100, num_levels=5)
#
#     print(f"G channel offset: {offsets[0]}")
#     print(f"R channel offset: {offsets[1]}")
#
#
# if __name__ == "__main__":
#     main()