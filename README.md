# CS180_Project1
Images of the Russian Empire: Colorizing the Prokudin-Gorskii photo collection


z1_all_tif.py
    this file allows me to convert everything to same type
    I just made them .tif so that when I save and load file there is no lossy compression
    but if need could make .jpg to save space
    these are all the images that i work with on the project
    NEED to have a subfolder ./data_tif/ for this to work

z2_ryan.py
    this file is important it has all the testing methods that the instructions wanted plus my extra credit stuff
    after running all I comment and labeled all of them and METHOD 1 (trivial stack), METHOD 4, METHOD 5, METHOD 6 were
    the ones that I decided to use as they had reasonable runtimes and correspond to everything in the ./render/ where each image
    number is in a folder with its index i.e. image 5 is folder ./render/5/ and then there is:

    001___original_icon.tif
    002___bw_1of3_blue_icon.tif
    003___bw_2of3_green_icon.tif
    004___bw_3of3_red_icon.tif
    005___sobel_1of3_blue_icon.tif
    006___sobel_2of3_green_icon.tif
    007___sobel_3of3_red_icon.tif
    008___trivial_stack__icon.tif
    009___trivial_stack_sobel__icon.tif
    014___SFSA_euclidean_stack__icon.tif
    015___SFSA_euclidean_stack_sobel__icon.tif
    016___PYRAMID_SFSA_euclidean_stack__icon.tif
    017___PYRAMID_SFSA_euclidean_stack_sobel__icon.tif
    018___PYRAMID_NORMAL_euclidean_stack__icon.tif
    019___PYRAMID_NORMAL_euclidean_stack_sobel__icon.tif
    render_notes.txt --> has run results metadata

    as these are the ones that I ran as others are slower with worse results make sure to
    uncomment the section that you want ... I could not think of better way as otherwise would need
    to rerender and that would waste time when I do not need them again

    To describe it in detail:
    METHOD 1 -- trivial stack --> is just stacking them after splitting them equally
    METHOD 2 -- euclidean stack --> is just using euclidean exhaustive search and is slow as described
    METHOD 3 -- normalized_cross_correlation stack --> same as METHOD 2 but just with NCC error function instead
    METHOD 4 -- euclidean stack w/ sobel filter to determine shift amount + crop --> got crazy speedup and great results without even putting in
    pyramid and later I put this into pyramid and it gets even faster with very little addition error, extra credit part for project with filter and crop from scratch
    METHOD 5 -- multiscale pyramid version -- filter + crop --> pyramid for METHOD 4
    METHOD 6 -- multiscale pyramid version -- normal --> normal part 2 of the project

    *IMPORTANT: Also if not mentioned all cropping uses crop_amnt = int(min(blue.shape)/3) as this seemed to be fine but more testing could easily tune this


z3_ryan.py
    This file has all the exhaustive search implementation functions with multicore and single core ones are in z4_ryan.py along with pyramid could multicore it but was getting complicated
    and they said that it would be fast anyway but really fast if you add that assuming you have more cores runtime/1 time versus runtime/#cores time

z4_ryan.py
    This file has single core ones are in along with pyramid implementation.


RENDER_VIDEO_FILES --> uncomment images and shifts that you want render ... this will change index though
    z5_ryan.py
        RENDER ALL BUT sculpture.tif frames for video all files share single core

    z6_ryan.py
        RENDER ALL BUT sculpture.tif frames for video each file gets single core

    z7_ryan.py
        CAN IGNORE but included for reference as tested sculpture.tif on it

    z8_ryan.py
        RENDER ALL AND sculpture.tif frames for video each file gets single core but only tested on sculpture.tif b/c other videos looked fine and took a long time to render so
        did not check for other but this should be the one you can use for all and ignore other RENDER_VIDEO_FILES (z5_ryan.py, z6_ryan.py, z7_ryan.py)
        but b/c ran others on these needed to include for replication, plus this is extra so figure it is okay



z9_ryan.py
    this file is just a test file that I used to test that the offsets produced
    gave good images


FOLDERS
    ./data
        has the original images

    ./data_tif
        has images all in .tif format ... ones used in my project

    ./frames
        has all frames for each image index

    ./render
        has all final renders for each image index

    ./videos
        has all videos generated for website


*IMPORTANT: if you do not make sure that each subfolder is there along with all index folders to avoid errors and there are no dot file to ensure runs properly
*IMPORTANT: on all multicore operations make sure that if there is error that cores matches with you computer and is not greater than jobs
*IMPORTANT: when I compress, I might change all .tif to .jpg so that I can fit it in the submission portal but should all be on github and website
*IMPORTANT: data showing improvement is also in the render_notes.txt for each image

github: ???
website: ???