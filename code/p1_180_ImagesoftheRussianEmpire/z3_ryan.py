# TODO: this file has all the exhaustive search implementation functions

import numpy as np
from multiprocessing import Pool, Manager
from tqdm import tqdm
import time

# ERROR FUNCTION 1
# used this because minimizing the sum of squared differences is equivalent to minimizing
# the Euclidean distance ... the square root is omitted to simplify the computation ... i.e. squared Euclidean distance
def euclidean_distance(base_image, shifted_image):
    return np.sum((base_image - shifted_image) ** 2)

# ERROR FUNCTION 2
def normalized_cross_correlation(base_image, shifted_image):
    base_norm = base_image / np.linalg.norm(base_image)
    shifted_norm = shifted_image / np.linalg.norm(shifted_image)
    return -np.sum(base_norm * shifted_norm)

# like np.roll but with 0 padding
def roll_with_padding(array, shift):
    y_shift, x_shift = shift
    result = np.roll(array, shift=y_shift, axis=0)
    result = np.roll(result, shift=x_shift, axis=1)

    if y_shift > 0:
        result[:y_shift, :] = 0
    elif y_shift < 0:
        result[y_shift:, :] = 0

    if x_shift > 0:
        result[:, :x_shift] = 0
    elif x_shift < 0:
        result[:, x_shift:] = 0

    return result

# apply the given offsets to green and red channels
def apply_shifts(blue, green, red, green_offset, red_offset):
    green_shifted = roll_with_padding(green, shift=green_offset)
    red_shifted = roll_with_padding(red, shift=red_offset)
    return blue, green_shifted, red_shifted

def align_chunk(args):
    base_image, image_to_align, y_range, max_offset, progress, idx, error_func = args
    total_iterations = (y_range[1] - y_range[0]) * (2 * max_offset + 1)
    current_iteration = 0

    best_offset = (0, 0)
    min_error = float('inf')

    for y_offset in range(y_range[0], y_range[1]):
        for x_offset in range(-max_offset, max_offset + 1):
            # TODO: IMPORTANT np.roll wraps around so want to change this so that it does not wrap and
            # instead just crops it with black which should be better for the error
            # function based on class notes
            # shifted_image = np.roll(image_to_align, shift=(y_offset, x_offset), axis=(0, 1))
            shifted_image = roll_with_padding(image_to_align, shift=(y_offset, x_offset))

            # add support for multiple different error functions
            # error = np.sum((base_image - shifted_image) ** 2)
            error = error_func(base_image, shifted_image)

            if error < min_error:
                min_error = error
                best_offset = (y_offset, x_offset)

            current_iteration += 1
            progress[idx] = current_iteration / total_iterations * 100

    return best_offset, min_error


def monitor_progress(progress):
    pbar_list = [tqdm(total=100, position=i, desc=f"Process {i + 1}") for i in range(len(progress))]
    while any(p < 100 for p in progress):
        for i, pbar in enumerate(pbar_list):
            pbar.n = progress[i]
            pbar.refresh()
        # time.sleep(1)
    for pbar in pbar_list:
        pbar.close()


def align_images_multicore(base_image, image_to_align, max_offset=15, num_processes=4, error_metric='euclidean'):
    assert (base_image.shape == image_to_align.shape)

    if error_metric == 'euclidean':
        print("euclidean")
        error_func = euclidean_distance
    elif error_metric == 'normalized_cross_correlation':
        print("normalized_cross_correlation")
        error_func = normalized_cross_correlation
    else:
        print("invalid error function ... default to euclidean_distance")
        error_func = euclidean_distance


    manager = Manager()
    progress = manager.list([0] * num_processes)

    chunk_size = (2 * max_offset + 1) // num_processes
    ranges = [(-max_offset + i * chunk_size, -max_offset + (i + 1) * chunk_size) for i in range(num_processes)]
    ranges[-1] = (ranges[-1][0], max_offset + 1)

    args = [(base_image, image_to_align, r, max_offset, progress, i, error_func) for i, r in enumerate(ranges)]

    with Pool(processes=num_processes) as pool:
        monitor = Pool(processes=1)
        monitor.apply_async(monitor_progress, (progress,))
        results = pool.starmap(align_chunk, [(arg,) for arg in args])
        pool.close()
        pool.join()
        monitor.close()
        monitor.join()

    best_offset = (0, 0)
    min_error = float('inf')
    for offset, error in results:
        if error < min_error:
            min_error = error
            best_offset = offset

    return best_offset