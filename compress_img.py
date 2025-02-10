#  Script taken from https://thepythoncode.com/article/compress-images-in-python 
## Edited for our purpose

### Script to compress images

#### Run by executing following line in terminal:
##### py compress_img.py "frames/fruits.mp4" -o "compressed_frames" -j -c 280 -r 0.277
##### compresses images from frames/fruits.mp4, stores in compressed_frames,
##### -j converts to jpg file, -c: crops 280 pixels from top and bottom, -r resizes height and width * 0.277

import os
from PIL import Image
import cv2

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def compress_img(image_path, output_folder, new_size_ratio=0.9, quality=90, width=None, height=None, to_jpg=True, crop=None):
    # load the image to memory
    img = Image.open(image_path)
    # print the original image shape
    print("[*] Image shape:", img.size)
    # get the original image size in bytes
    image_size = os.path.getsize(image_path)
    # print the size before compression/resizing
    print("[*] Size before compression:", get_size_format(image_size))

    if crop:
        width, height = img.size 
        img = img.crop((0, crop, width, height - crop))
        print("[+] Cropped Image shape:", img.size)

    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.LANCZOS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.LANCZOS)
        # print new image shape
        print("[+] New Image shape:", img.size)
    # split the filename and extension
    filename, ext = os.path.splitext(os.path.basename(image_path))
    # make new filename appending _compressed to the original file name
    if to_jpg:
        # change the extension to JPEG
        new_filename = f"{filename}_compressed.jpg"
    else:
        # retain the same extension of the original image
        new_filename = f"{filename}_compressed{ext}"

    new_filepath = os.path.join(output_folder, new_filename)

    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filepath, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filepath, quality=quality, optimize=True)
    print("[+] New file saved:", new_filepath, new_filename)
    # get the new image size in bytes
    new_image_size = os.path.getsize(new_filepath)
    # print the new size in a good format
    print("[+] Size after compression:", get_size_format(new_image_size))
    # calculate the saving bytes
    saving_diff = new_image_size - image_size
    # print the saving percentage
    print(f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")
    

def process_folder(folder, output_folder, resize_ratio, quality, width, height, to_jpg, crop):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            file_path = os.path.join(folder, filename)
            compress_img(file_path, output_folder, resize_ratio, quality, width, height, to_jpg, crop)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simple Python script for compressing and resizing images")
    parser.add_argument("folder", help="Folder containing images to compress")
    parser.add_argument("-o", "--output", default="compressed_images", help="Output folder for compressed images")
    parser.add_argument("-j", "--to-jpg", action="store_true", help="Whether to convert the image to the JPEG format")
    parser.add_argument("-q", "--quality", type=int, help="Quality ranging from a minimum of 0 (worst) to a maximum of 95 (best). Default is 90", default=90)
    parser.add_argument("-r", "--resize-ratio", type=float, help="Resizing ratio from 0 to 1, setting to 0.5 will multiply width & height of the image by 0.5. Default is 1.0", default=1.0)
    parser.add_argument("-w", "--width", type=int, help="The new width image, make sure to set it with the `height` parameter")
    parser.add_argument("-hh", "--height", type=int, help="The new height for the image, make sure to set it with the `width` parameter")
    parser.add_argument("-c", "--crop", type=int, help="Crop this many pixels from the top and bottom before resizing")

    args = parser.parse_args()
    # print the passed arguments
    print("="*50)
    #print("[*] Image:", args.image)
    print("[*] To JPEG:", args.to_jpg)
    print("[*] Quality:", args.quality)
    print("[*] Resizing ratio:", args.resize_ratio)
    print("[*] Crop:", args.crop)
    if args.width and args.height:
        print("[*] Width:", args.width)
        print("[*] Height:", args.height)
    print("="*50)
    # compress the image
    process_folder(args.folder, args.output, args.resize_ratio, args.quality, args.width, args.height, args.to_jpg, args.crop)


