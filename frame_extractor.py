import cv2
import xml.etree.ElementTree as ET
import os

video_name = 'fruits.mp4'
xml_path = 'annotations/annotations_train.xml'
video_path = 'videos/fruits.mp4'

def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    frame_numbers = []

    for track in root.findall('track'):
        if track.attrib['label'] == 'orange' or track.attrib['label'] == 'apple' or track.attrib['label'] == 'banana':
            for box in track.findall('./box'):
                frame_numbers.append(int(box.attrib['frame']))
    return frame_numbers


def create_frames_directory(base_path, video_name):
    frames_dir = os.path.join(base_path, f'{video_name}')
    if not os.path.exists(frames_dir):
        os.makedirs(frames_dir)
    return frames_dir


def extract_frames(video_path, frame_numbers, output_dir):
    cap = cv2.VideoCapture(video_path)
    current_frame = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if current_frame in frame_numbers:
            frame_path = os.path.join(output_dir, f'frame_{current_frame}.png')
            print(f"Saving frame: {frame_path}")
            cv2.imwrite(frame_path, frame)

        current_frame += 1

    cap.release()


def main(video_name, video_path, xml_path):
    frame_numbers = parse_xml(xml_path)
    frames_dir = create_frames_directory('frames', video_name)
    extract_frames(video_path, frame_numbers, frames_dir)


main(video_name, video_path, xml_path)
