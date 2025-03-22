import xml.etree.ElementTree as ET
from collections import defaultdict

tree = ET.parse('annotations/banana_white_desk.xml')
root = tree.getroot()

frames_dict = defaultdict(list)

for track in root.findall('track'):
    label = track.get('label', '')
    for box in track.findall('box'):
        frame = box.get('frame')
        duplicate = False
        for existing_box in frames_dict[frame]:
            if existing_box.get('label', label) == label:
                duplicate = True
                break
        if not duplicate:
            box.set('label', label)
            frames_dict[frame].append(box)

for track in root.findall('track'):
    root.remove(track)

new_track = ET.Element('track', attrib={'id': '0', 'label': 'merged'})
for frame in sorted(frames_dict.keys(), key=lambda x: int(x)):
    for box in frames_dict[frame]:
        new_track.append(box)

root.append(new_track)

tree.write('banana_white_desk.xml', encoding='utf-8', xml_declaration=True)