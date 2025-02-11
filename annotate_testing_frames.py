import cv2
import os
import xml.etree.ElementTree as ET
from pascal_voc import write_pascal_voc, append_object_to_pascal_voc
from helpers import drawbbox

annotation_path = 'annotations/annotations_test.xml'

exported_annotations_folderpath = 'annotations/annotations_test'
os.makedirs(exported_annotations_folderpath, exist_ok=True)

tree = ET.parse(annotation_path)
root = tree.getroot()

for image in root.findall('image'):
    prev_frame = None
    frame_num = image.attrib['id']
    file_name = image.attrib['name']
    for box in image.findall('box'):
        label = box.attrib['label']
        print(f"Processing frame: {frame_num}")
        