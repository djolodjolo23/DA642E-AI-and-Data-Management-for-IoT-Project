import xml.etree.ElementTree as ET
import os
import argparse


def parse_xml_annotation_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist")

    tree = ET.parse(file_path)
    root = tree.getroot()
    result = {}

    size = root.find('size')
    result['size'] = {
        'width': size.find('width').text,
        'height': size.find('height').text
    }

    result['object'] = []
    for obj in root.findall('object'):
        obj_data = {
            'name': obj.find('name').text,
            'bndbox': {
                'xmin': obj.find('bndbox/xmin').text,
                'ymin': obj.find('bndbox/ymin').text,
                'xmax': obj.find('bndbox/xmax').text,
                'ymax': obj.find('bndbox/ymax').text
            }
        }
        result['object'].append(obj_data)

    return result


def calculate_bbox_area_percentage(annotation_data):
    width = int(annotation_data['size']['width'])
    height = int(annotation_data['size']['height'])
    total_image_area = width * height

    results = []
    for obj in annotation_data['object']:
        name = obj['name']
        bbox = obj['bndbox']

        x_min = float(bbox['xmin'])
        y_min = float(bbox['ymin'])
        x_max = float(bbox['xmax'])
        y_max = float(bbox['ymax'])

        box_width = x_max - x_min
        box_height = y_max - y_min
        box_area = box_width * box_height

        percentage = (box_area / total_image_area) * 100

        results.append({
            'name': name,
            'area_pixels': box_area,
            'area_percentage': percentage
        })

    return results


def process_annotation_file(file_path):
    """Process a single annotation file and print results"""
    try:
        annotation_data = parse_xml_annotation_from_file(file_path)

        results = calculate_bbox_area_percentage(annotation_data)

        print(f"\nResults for: {os.path.basename(file_path)}")
        print(f"Image size: {annotation_data['size']['width']}x{annotation_data['size']['height']} pixels")
        print("Bounding Box Areas:")

        for obj in results:
            print(f"- {obj['name']}:")
            print(f"  Area: {obj['area_pixels']:.2f} pixels²")
            print(f"  Percentage of image: {obj['area_percentage']:.2f}%")

        total_percentage = sum(obj['area_percentage'] for obj in results)
        print(f"\nTotal area covered by all objects: {total_percentage:.2f}%")

        return results

    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate bounding box area percentages from XML annotation files")
    parser.add_argument("file_path", help="Path to XML annotation file")
    parser.add_argument("--batch", help="Directory containing multiple XML files to process", default=None)

    args = parser.parse_args()

    if args.batch:
        if not os.path.isdir(args.batch):
            print(f"Error: {args.batch} is not a directory")
            exit(1)

        xml_files = [os.path.join(args.batch, f) for f in os.listdir(args.batch) if f.endswith('.xml')]

        if not xml_files:
            print(f"No XML files found in {args.batch}")
            exit(0)

        print(f"Processing {len(xml_files)} XML files from {args.batch}")
        for xml_file in xml_files:
            process_annotation_file(xml_file)

    else:
        process_annotation_file(args.file_path)