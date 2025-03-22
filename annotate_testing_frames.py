import cv2
import os
import xml.etree.ElementTree as ET
from pascal_voc import write_pascal_voc, append_object_to_pascal_voc
from helpers import drawbbox

target_image_width = 128
target_image_height = 128

annotation_path = 'annotations/testset-orange-2/annotations.xml'

compressed_testing_folder_path = f'compressed_testing/testset-orange-2/frames_{target_image_height} x {target_image_width}'
exported_annotations_folderpath = 'compressed_testing/testset-orange-2/annotations'
os.makedirs(exported_annotations_folderpath, exist_ok=True)
os.makedirs(compressed_testing_folder_path, exist_ok=True)

tree = ET.parse(annotation_path)
root = tree.getroot()


for image in root.findall('image'):
    on_first_frame = True
    frame_num = image.attrib['id']
    file_name = image.attrib['name']
    for box in image.findall('box'):
        label = box.attrib['label']
        print(f"Processing frame: {frame_num}")

        image_path = os.path.join(f'testing/images_of_orange (2)/{file_name}')
        if not os.path.exists(image_path):
            continue

        xtl, ytl, xbr, ybr = [float(box.attrib[attr]) for attr in ['xtl', 'ytl', 'xbr', 'ybr']]

        original_image = cv2.imread(image_path)

        (h, w) = original_image.shape[:2]

        aspect_ratio = w / h # width / height, to maintain the aspect ratio of the original image

        new_width = int(aspect_ratio * target_image_width) # aspect_ratio * target_imag

        resized_image = cv2.resize(original_image, (new_width, target_image_height))

        if new_width > target_image_width:
            start_x = (new_width - target_image_width) // 2
            cropped_image = resized_image[:, start_x:start_x + target_image_width]
        else:
            cropped_image = resized_image

        cv2.imwrite(f'{compressed_testing_folder_path}/{file_name}', cropped_image)

        resize_ratio = target_image_width / original_image.shape[0]

        new_xtl = xtl * resize_ratio - start_x if new_width > target_image_width else xtl * resize_ratio
        new_ytl = ytl * resize_ratio
        new_xbr = xbr * resize_ratio - start_x if new_width > target_image_width else xbr * resize_ratio
        new_ybr = ybr * resize_ratio


        if new_xtl < 0: # if xtl is negative, set it to 0
            new_xtl = 0
        if new_ytl < 0: # if ytl is negative, set it to 0
            new_ytl = 0
        if new_xbr > target_image_width: # if xbr is greater than the target image width, set it to the target image width, because bbox reaches maximum width point, which is the target image width
            new_xbr = target_image_width
        if new_ybr > target_image_height: # if ybr is greater than the target image height, set it to the target image height, because bbox reaches maximum height point, which is the target image height
            new_ybr = target_image_height

        new_file_name = file_name.rsplit('.jpg', 1)[0] + '.png'
        xml_path = f'{exported_annotations_folderpath}/{new_file_name}.xml'

        if not on_first_frame:
            append_object_to_pascal_voc(xml_path, label, new_xtl, new_ytl, new_xbr, new_ybr)
        else:
            write_pascal_voc(xml_path, file_name, label, target_image_width, target_image_height, new_xtl, new_ytl, new_xbr, new_ybr)
            on_first_frame = False

        #drawbbox(compressed_testing_folder_path, file_name, new_xtl, new_ytl, new_xbr, new_ybr)