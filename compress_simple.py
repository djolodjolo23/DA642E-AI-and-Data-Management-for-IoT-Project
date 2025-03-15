import cv2
import os
import xml.etree.ElementTree as ET
from pascal_voc import write_pascal_voc, append_object_to_pascal_voc
from helpers import drawbbox


target_image_width = 128
target_image_height = 128
video_name = 'fruits.mp4'
annotation_path = 'output.xml'

compressed_folder_path = f'compressed/{video_name}/frames_{target_image_width} x {target_image_height}'
compressed_annotations_folderpath = f'compressed/{video_name}/annotations_{target_image_width} x {target_image_height}'
os.makedirs(compressed_folder_path, exist_ok=True)
os.makedirs(compressed_annotations_folderpath, exist_ok=True)

print(f"Processing annotations_CVAT from: {annotation_path}")

tree = ET.parse(annotation_path)
root = tree.getroot()

for track in root.findall('.//track'):
    prev_frame = None

    for box in track.findall('box'):
        frame_num = box.attrib['frame']
        label = box.attrib['label']
        print(f"Processing frame: {frame_num}")

        image_path = os.path.join(f'frames/{video_name}/frame_{frame_num}.png')
        if not os.path.exists(image_path):
            continue

        original_image = cv2.imread(image_path)
        xtl, ytl, xbr, ybr = [float(box.attrib[attr]) for attr in ['xtl', 'ytl', 'xbr', 'ybr']]

        if frame_num == '204':
            print("debug")

        (h, w) = original_image.shape[:2]
        aspect_ratio = h / w # height / width, to maintain the aspect ratio of the original image

        new_height = int(aspect_ratio * target_image_height) # aspect_ratio * target_imag

        resized_image = cv2.resize(original_image, (target_image_width, new_height))


        if new_height > target_image_height:
            start_y = (new_height - target_image_height) // 2
            cropped_image = resized_image[start_y:start_y + target_image_height, :]
        else:
            cropped_image = resized_image


        cv2.imwrite(f'{compressed_folder_path}/frame_{frame_num}.png', cropped_image)
        print(f"Image saved to: {compressed_folder_path}/frame_{frame_num}.png")

        resize_ratio = target_image_width / original_image.shape[1]

        new_xtl = xtl * resize_ratio
        new_ytl = (ytl * resize_ratio) - start_y if new_height > target_image_height else ytl * resize_ratio
        new_xbr = xbr * resize_ratio
        new_ybr = (ybr * resize_ratio) - start_y if new_height > target_image_height else ybr * resize_ratio

        if new_xtl < 0: # if xtl is negative, set it to 0
            new_xtl = 0
        if new_ytl < 0: # if ytl is negative, set it to 0
            new_ytl = 0
        if new_xbr > target_image_width: # if xbr is greater than the target image width, set it to the target image width, because bbox reaches maximum width point, which is the target image width
            new_xbr = target_image_width
        if new_ybr > target_image_height: # if ybr is greater than the target image height, set it to the target image height, because bbox reaches maximum height point, which is the target image height
            new_ybr = target_image_height

        xml_path = f'{compressed_annotations_folderpath}/frame_{frame_num}.xml'
        if prev_frame == frame_num:
            append_object_to_pascal_voc(xml_path, label, new_xtl, new_ytl, new_xbr, new_ybr)
        else:
            write_pascal_voc(f'{compressed_annotations_folderpath}/frame_{frame_num}.xml',
             f'frame_{frame_num}.png', label,
             target_image_width, target_image_height, new_xtl, new_ytl, new_xbr, new_ybr)

        prev_frame = frame_num

        # for debugging, draw the bounding box on the image
        #drawbbox(compressed_folder_path, frame_num, new_xtl, new_ytl, new_xbr, new_ybr)

