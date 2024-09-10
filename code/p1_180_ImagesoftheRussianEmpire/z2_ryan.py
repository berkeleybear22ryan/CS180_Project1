import numpy as np
from skimage import io
from scipy.signal import convolve2d
from z3_ryan import align_images_multicore, apply_shifts
from z4_ryan import align_channels
import time


# function that loads and splits the image
def load_and_split_image(image_path):
    img = io.imread(image_path)
    third_height = img.shape[0] // 3

    blue = img[:third_height]
    green = img[third_height:2 * third_height]
    red = img[2 * third_height:]

    # make sure that they are all the proper dimensions
    if red.shape[0] > third_height:
        red = red[:third_height]

    return blue, green, red

# functions that removes
# top amount of pixels from top,
# bottom amount of pixels from bottom and ...
def trim_borders(array, top, bottom, left, right):
    if array.ndim != 2:
        raise ValueError("Input array must be 2D.")
    new_top = top
    new_bottom = array.shape[0] - bottom
    new_left = left
    new_right = array.shape[1] - right
    trimmed_array = array[new_top:new_bottom, new_left:new_right]
    return trimmed_array

# custom sobel filter implementation
def sobel_filter(image):
    Gx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]])
    Gy = np.array([[-1, -2, -1],
                   [0,  0,  0],
                   [1,  2,  1]])

    sobel_x = convolve2d(image, Gx, mode='same', boundary='symm')
    sobel_y = convolve2d(image, Gy, mode='same', boundary='symm')

    sobel_mag = np.sqrt(sobel_x**2 + sobel_y**2)

    # change this to adjust the filter
    # sobel_mag = np.power(sobel_mag, 0.5)

    # handle the division by 0 when shifting
    denominator = (np.max(sobel_mag) - np.min(sobel_mag))
    if denominator == 0:
        denominator = denominator + 0.0000001
    sobel_mag = (sobel_mag - np.min(sobel_mag)) / denominator
    return sobel_mag


if __name__ == '__main__':
    # TODO: part 1 -- setup the files to go through and loop through each one
    source_directory = './data_tif/'
    save_directory = './render/'
    num_processes = 24
    # make sure that the max_offset >= num_processes
    # max_offset = 150 # -- all except 7 (melons.tif),11 (self_portrait.tif)
    # max_offset = 300
    max_offset = 200
    assert (max_offset >= num_processes)
    # comment based on which one you want to use

    # images = [
    #     'cathedral.tif', 'church.tif', 'emir.tif', 'harvesters.tif',
    #     'icon.tif', 'lady.tif', 'melons.tif', 'monastery.tif',
    #     'onion_church.tif', 'sculpture.tif', 'self_portrait.tif',
    #     'three_generations.tif', 'tobolsk.tif', 'train.tif'
    # ]
    # images = ['melons.tif', 'self_portrait.tif']
    # images = [
    #     'z_extra1.tif', 'z_extra2.tif', 'z_extra3.tif', 'z_extra4.tif'
    # ]
    images = ['z_extra2.tif']

    i = 1
    for filename in images:
        image_path = source_directory + filename

        print("\n\n\n\n")
        print(image_path + " " + f"{i}/{len(images)}")

        # TODO: part 2 -- separate the image into 3 different parts so that we can work with each channel
        blue, green, red = load_and_split_image(image_path)

        # save the original image img = io.imread(image_path)
        io.imsave(save_directory + f"{i}/" + "001___original_" + filename, io.imread(image_path))

        # save the three files to the for each image in bw
        io.imsave(save_directory + f"{i}/" + "002___bw_1of3_blue_" + filename, blue)
        io.imsave(save_directory + f"{i}/" + "003___bw_2of3_green_" + filename, green)
        io.imsave(save_directory + f"{i}/" + "004___bw_3of3_red_" + filename, red)

        io.imsave(save_directory + f"{i}/" + "005___sobel_1of3_blue_" + filename, (sobel_filter(blue) * 65535).astype(np.uint16))
        io.imsave(save_directory + f"{i}/" + "006___sobel_2of3_green_" + filename, (sobel_filter(green) * 65535).astype(np.uint16))
        io.imsave(save_directory + f"{i}/" + "007___sobel_3of3_red_" + filename, (sobel_filter(red) * 65535).astype(np.uint16))








        # TODO: MAIN PART ...

        # TODO: part 3 -- stacking the images based on different methods

        # # TODO: METHOD 1 -- trivial stack -- uncomment to use
        # # now show the trivial stack
        # start_time = time.time()
        # filename_nofilter = save_directory + f"{i}/" + "008___trivial_stack__" + filename
        # filename_yesfilter = save_directory + f"{i}/" + "009___trivial_stack_sobel__" + filename
        # io.imsave(filename_nofilter, np.stack((red, green, blue), axis=-1))
        # io.imsave(filename_yesfilter, np.stack(((sobel_filter(red) * 65535).astype(np.uint16), (sobel_filter(green) * 65535).astype(np.uint16), (sobel_filter(blue) * 65535).astype(np.uint16)), axis=-1))
        # offset_green = (0, 0)
        # offset_red = (0, 0)
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        #
        # with open(f"{save_directory}" + f"{i}/" + "render_notes.txt", 'w') as file:
        #     file.write(f"NO FILTER, NO CROP, trivial stack -- method 1\n")
        #     file.write(f"associated files: {filename_nofilter, filename_yesfilter})\n")
        #     file.write(f"max_offset: {max_offset}\n")
        #     file.write(f"Offset for Green Channel: {offset_green}\n")
        #     file.write(f"Offset for Red Channel: {offset_red}\n")
        #     file.write(f"Elapsed time: {elapsed_time} seconds\n")
        #     file.write("\n\n\n")





        # # -- exhaustive search
        # # TODO: METHOD 2 -- euclidean stack -- uncomment to use
        # start_time = time.time()
        # # now do the exhaustive search to see if you can find the shift_y and shift_x amounts (shift_y, shift_x)
        # # with Euclidean distance
        # offset_green = align_images_multicore(blue, green, max_offset=max_offset, num_processes=num_processes, error_metric='euclidean')
        # print(f"max_offset: {max_offset}\nOffset for Green Channel:", offset_green)
        # offset_red = align_images_multicore(blue, red, max_offset=max_offset, num_processes=num_processes, error_metric='euclidean')
        # print(f"max_offset: {max_offset}\nOffset for Red Channel:", offset_red)
        #
        # filename_nofilter = save_directory + f"{i}/" + "010___euclidean_stack__" + filename
        # filename_yesfilter = save_directory + f"{i}/" + "011___euclidean_stack_sobel__" + filename
        #
        # blue_shifted, green_shifted, red_shifted = apply_shifts(blue, green, red, offset_green, offset_red)
        # rgb_image_nofilter = np.stack((red_shifted, green_shifted, blue_shifted), axis=-1)
        # rgb_image_yesfilter = np.stack(((sobel_filter(red_shifted) * 65535).astype(np.uint16), (sobel_filter(green_shifted) * 65535).astype(np.uint16), (sobel_filter(blue_shifted) * 65535).astype(np.uint16)), axis=-1)
        # io.imsave(filename_nofilter, rgb_image_nofilter)
        # io.imsave(filename_yesfilter, rgb_image_yesfilter)
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        #
        # # write the offset_green and offset_red to txt file
        # with open(f"{save_directory}" + f"{i}/" + "render_notes.txt", 'a') as file:
        #     file.write(f"NO FILTER, NO CROP, euclidean stack -- method 2\n")
        #     file.write(f"associated files: {filename_nofilter, filename_yesfilter})\n")
        #     file.write(f"max_offset: {max_offset}\n")
        #     file.write(f"Offset for Green Channel: {offset_green}\n")
        #     file.write(f"Offset for Red Channel: {offset_red}\n")
        #     file.write(f"Elapsed time: {elapsed_time} seconds\n")
        #     file.write("\n\n\n")


        # # -- exhaustive search
        # # TODO: METHOD 3 -- normalized_cross_correlation stack -- uncomment to use
        # start_time = time.time()
        # # now do the exhaustive search to see if you can find the shift_y and shift_x amounts (shift_y, shift_x)
        # # with normalized cross-correlation
        # offset_green = align_images_multicore(blue, green, max_offset=max_offset, num_processes=num_processes,
        #                                       error_metric='normalized_cross_correlation')
        # print(f"max_offset: {max_offset}\nOffset for Green Channel:", offset_green)
        # offset_red = align_images_multicore(blue, red, max_offset=max_offset, num_processes=num_processes,
        #                                     error_metric='normalized_cross_correlation')
        # print(f"max_offset: {max_offset}\nOffset for Red Channel:", offset_red)
        #
        # filename_nofilter = save_directory + f"{i}/" + "012___normalized_cross_correlation_stack__" + filename
        # filename_yesfilter = save_directory + f"{i}/" + "013___normalized_cross_correlation_stack_sobel__" + filename
        #
        # blue_shifted, green_shifted, red_shifted = apply_shifts(blue, green, red, offset_green, offset_red)
        # rgb_image_nofilter = np.stack((red_shifted, green_shifted, blue_shifted), axis=-1)
        # rgb_image_yesfilter = np.stack(((sobel_filter(red_shifted) * 65535).astype(np.uint16),
        #                                 (sobel_filter(green_shifted) * 65535).astype(np.uint16),
        #                                 (sobel_filter(blue_shifted) * 65535).astype(np.uint16)), axis=-1)
        #
        # io.imsave(filename_nofilter, rgb_image_nofilter)
        # io.imsave(filename_yesfilter, rgb_image_yesfilter)
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        #
        # # write the offset_green and offset_red to txt file
        # with open(f"{save_directory}" + f"{i}/" + "render_notes.txt", 'a') as file:
        #     file.write(f"NO FILTER, NO CROP, normalized_cross_correlation stack -- method 3\n")
        #     file.write(f"associated files: {filename_nofilter, filename_yesfilter})\n")
        #     file.write(f"max_offset: {max_offset}\n")
        #     file.write(f"Offset for Green Channel: {offset_green}\n")
        #     file.write(f"Offset for Red Channel: {offset_red}\n")
        #     file.write(f"Elapsed time: {elapsed_time} seconds\n")
        #     file.write("\n\n\n")







        # -- really good, constrained exhaustive search w/ filter
        # TODO: METHOD 4 -- euclidean stack w/ sobel filter to determine shift amount + crop -- uncomment to use
        # SFSA: sobel filter + shift amount
        start_time = time.time()
        # now do the exhaustive search to see if you can find the shift_y and shift_x amounts (shift_y, shift_x)
        # with Euclidean distance

        # DEFUALT FOR ALL IS /3
        crop_amnt = int(min(blue.shape)/3)
        # crop_amnt = int(min(blue.shape)/2)


        print(f"crop_amount: {crop_amnt}")
        offset_green = align_images_multicore(trim_borders(sobel_filter(blue), crop_amnt, crop_amnt, crop_amnt, crop_amnt), trim_borders(sobel_filter(green), crop_amnt, crop_amnt, crop_amnt, crop_amnt), max_offset=max_offset, num_processes=num_processes,
                                              error_metric='euclidean')
        print(f"max_offset: {max_offset}\nOffset for Green Channel:", offset_green)
        offset_red = align_images_multicore(trim_borders(sobel_filter(blue), crop_amnt, crop_amnt, crop_amnt, crop_amnt), trim_borders(sobel_filter(red), crop_amnt, crop_amnt, crop_amnt, crop_amnt), max_offset=max_offset, num_processes=num_processes,
                                            error_metric='euclidean')
        print(f"max_offset: {max_offset}\nOffset for Red Channel:", offset_red)

        filename_nofilter = save_directory + f"{i}/" + "014___SFSA_euclidean_stack__" + filename
        filename_yesfilter = save_directory + f"{i}/" + "015___SFSA_euclidean_stack_sobel__" + filename

        blue_shifted, green_shifted, red_shifted = apply_shifts(blue, green, red, offset_green, offset_red)
        rgb_image_nofilter = np.stack((red_shifted, green_shifted, blue_shifted), axis=-1)
        rgb_image_yesfilter = np.stack(((sobel_filter(red_shifted) * 65535).astype(np.uint16),
                                        (sobel_filter(green_shifted) * 65535).astype(np.uint16),
                                        (sobel_filter(blue_shifted) * 65535).astype(np.uint16)), axis=-1)
        io.imsave(filename_nofilter, rgb_image_nofilter)
        io.imsave(filename_yesfilter, rgb_image_yesfilter)
        end_time = time.time()
        elapsed_time = end_time - start_time

        # write the offset_green and offset_red to txt file
        with open(f"{save_directory}" + f"{i}/" + "render_notes.txt", 'a') as file:
            file.write(f"YES FILTER, YES CROP, euclidean stack -- method 4\n")
            file.write(f"associated files: {filename_nofilter, filename_yesfilter})\n")
            file.write(f"max_offset: {max_offset}\n")
            file.write(f"crop_amnt: {crop_amnt}\n")
            file.write(f"Offset for Green Channel: {offset_green}\n")
            file.write(f"Offset for Red Channel: {offset_red}\n")
            file.write(f"Elapsed time: {elapsed_time} seconds\n")
            file.write("\n\n\n")






        # # TODO: METHOD 5 -- multiscale pyramid version -- filter + crop
        # start_time = time.time()
        # # now do the multiscale pyramid version search to see if you can find the shift_y and shift_x amounts (shift_y, shift_x)
        # # with Euclidean distance
        # crop_amnt = int(min(blue.shape)/3)
        # print(f"crop_amount: {crop_amnt}")
        #
        # image = np.stack(
        #     (trim_borders(sobel_filter(blue), crop_amnt, crop_amnt, crop_amnt, crop_amnt),
        #      trim_borders(sobel_filter(green), crop_amnt, crop_amnt, crop_amnt, crop_amnt),
        #      trim_borders(sobel_filter(red), crop_amnt, crop_amnt, crop_amnt, crop_amnt)), axis=-1)
        #
        # # make sure the window is not larger than res after crop o/w will error
        # iw = 100
        # nl = 5
        # result, offsets = align_channels(image, initial_window=iw, num_levels=nl)
        # offset_green = offsets[0]
        # offset_red = offsets[1]
        # print(f"max_offset: {max_offset}\nOffset for Green Channel:", offset_green)
        # print(f"max_offset: {max_offset}\nOffset for Red Channel:", offset_red)
        #
        # filename_nofilter = save_directory + f"{i}/" + "016___PYRAMID_SFSA_euclidean_stack__" + filename
        # filename_yesfilter = save_directory + f"{i}/" + "017___PYRAMID_SFSA_euclidean_stack_sobel__" + filename
        #
        # blue_shifted, green_shifted, red_shifted = apply_shifts(blue, green, red, offset_green, offset_red)
        # rgb_image_nofilter = np.stack((red_shifted, green_shifted, blue_shifted), axis=-1)
        # rgb_image_yesfilter = np.stack(((sobel_filter(red_shifted) * 65535).astype(np.uint16),
        #                                 (sobel_filter(green_shifted) * 65535).astype(np.uint16),
        #                                 (sobel_filter(blue_shifted) * 65535).astype(np.uint16)), axis=-1)
        # io.imsave(filename_nofilter, rgb_image_nofilter)
        # io.imsave(filename_yesfilter, rgb_image_yesfilter)
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        #
        # # write the offset_green and offset_red to txt file
        # with open(f"{save_directory}" + f"{i}/" + "render_notes.txt", 'a') as file:
        #     file.write(f"YES FILTER, YES CROP, YES PYRAMID, euclidean stack -- method 5\n")
        #     file.write(f"associated files: {filename_nofilter, filename_yesfilter})\n")
        #     file.write(f"max_offset: {max_offset}\n")
        #     file.write(f"crop_amnt: {crop_amnt}\n")
        #     file.write(f"initial_window: {iw}\n")
        #     file.write(f"num_levels: {nl}\n")
        #     file.write(f"Offset for Green Channel: {offset_green}\n")
        #     file.write(f"Offset for Red Channel: {offset_red}\n")
        #     file.write(f"Elapsed time: {elapsed_time} seconds\n")
        #     file.write("\n\n\n")



        # # TODO: METHOD 6 -- multiscale pyramid version -- normal
        # start_time = time.time()
        # # now do the multiscale pyramid version search to see if you can find the shift_y and shift_x amounts (shift_y, shift_x)
        # # with Euclidean distance
        # crop_amnt = 0
        # print(f"crop_amount: {crop_amnt}")
        #
        # image = np.stack(
        #     (trim_borders(blue, crop_amnt, crop_amnt, crop_amnt, crop_amnt),
        #      trim_borders(green, crop_amnt, crop_amnt, crop_amnt, crop_amnt),
        #      trim_borders(red, crop_amnt, crop_amnt, crop_amnt, crop_amnt)), axis=-1)
        #
        # iw = 100
        # nl = 5
        # result, offsets = align_channels(image, initial_window=iw, num_levels=nl)
        # offset_green = offsets[0]
        # offset_red = offsets[1]
        # print(f"max_offset: {max_offset}\nOffset for Green Channel:", offset_green)
        # print(f"max_offset: {max_offset}\nOffset for Red Channel:", offset_red)
        #
        # filename_nofilter = save_directory + f"{i}/" + "018___PYRAMID_NORMAL_euclidean_stack__" + filename
        # filename_yesfilter = save_directory + f"{i}/" + "019___PYRAMID_NORMAL_euclidean_stack_sobel__" + filename
        #
        # blue_shifted, green_shifted, red_shifted = apply_shifts(blue, green, red, offset_green, offset_red)
        # rgb_image_nofilter = np.stack((red_shifted, green_shifted, blue_shifted), axis=-1)
        # rgb_image_yesfilter = np.stack(((sobel_filter(red_shifted) * 65535).astype(np.uint16),
        #                                 (sobel_filter(green_shifted) * 65535).astype(np.uint16),
        #                                 (sobel_filter(blue_shifted) * 65535).astype(np.uint16)), axis=-1)
        # io.imsave(filename_nofilter, rgb_image_nofilter)
        # io.imsave(filename_yesfilter, rgb_image_yesfilter)
        # end_time = time.time()
        # elapsed_time = end_time - start_time
        #
        # # write the offset_green and offset_red to txt file
        # with open(f"{save_directory}" + f"{i}/" + "render_notes.txt", 'a') as file:
        #     file.write(f"NO FILTER, NO CROP, YES PYRAMID, euclidean stack -- method 6\n")
        #     file.write(f"associated files: {filename_nofilter, filename_yesfilter})\n")
        #     file.write(f"max_offset: {max_offset}\n")
        #     file.write(f"crop_amnt: {crop_amnt}\n")
        #     file.write(f"initial_window: {iw}\n")
        #     file.write(f"num_levels: {nl}\n")
        #     file.write(f"Offset for Green Channel: {offset_green}\n")
        #     file.write(f"Offset for Red Channel: {offset_red}\n")
        #     file.write(f"Elapsed time: {elapsed_time} seconds\n")
        #     file.write("\n\n\n")







        i += 1









