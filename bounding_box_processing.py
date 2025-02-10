import cv2
import xml.etree.ElementTree as ET
import os
import re

# File paths
xml_path = "output.xml"
annotation_path = "annotations/rescaled_boxes"  # Folder to save annotation files
compressed_frames_path = "compressed_frames"  # Folder with compressed images
output_path = "processed_frames"  # New folder to save processed images


# Ensure output folders exists
os.makedirs(output_path, exist_ok=True)
os.makedirs(annotation_path, exist_ok=True)

# Read XML and parse bounding boxes
def parse_bboxes(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    bboxes = []
    
    for box in root.findall(".//box"):  
        frame = int(box.get("frame"))  
        xtl = float(box.get("xtl"))
        ytl = float(box.get("ytl"))
        xbr = float(box.get("xbr"))
        ybr = float(box.get("ybr"))
        label = box.get("label")

        keyframe = box.get("keyframe")
        outside = box.get("outside")
        occluded = box.get("occluded")
        z_order = box.get("z_order")

        bboxes.append((frame, xtl, ytl, xbr, ybr, label, keyframe, outside, occluded, z_order))
    
    return bboxes

# Extract frame number from filename (e.g., "frame_0_compressed.jpg" : 0)
def get_frame_number(filename):
    match = re.search(r'frame_(\d+)', filename)
    return int(match.group(1)) if match else None

# Scale bounding boxes after cropping
def scale_bboxes(bboxes, scale_x, scale_y, crop_top, target_frame):
    scaled_bboxes = []
    
    for frame, xtl, ytl, xbr, ybr, label, keyframe, outside, occluded, z_order in bboxes:
        if frame != target_frame:
            continue  # Skip bounding boxes from other frames

        # Adjust Y-coordinates for cropping
        ytl_adj = ytl - crop_top
        ybr_adj = ybr - crop_top

        # Scale coordinates, ## You may want to switch int() with round()
        xtl_new = int(xtl * scale_x)
        ytl_new = int(ytl_adj * scale_y)
        xbr_new = int(xbr * scale_x)
        ybr_new = int(ybr_adj * scale_y)

        scaled_bboxes.append((frame, xtl_new, ytl_new, xbr_new, ybr_new, label, keyframe, outside, occluded, z_order))
    
    return scaled_bboxes

# Draw bounding boxes
def draw_bboxes(image, bboxes):
    for xtl, ytl, xbr, ybr, *_ in bboxes:
        color = (0, 255, 0)  # Green box
        thickness = 1
        cv2.rectangle(image, (xtl, ytl), (xbr, ybr), color, thickness)

    return image


# Create an XML file for each processed frame
def save_bboxes_to_xml(frame_number, bboxes, annotation_path):
    annotation = ET.Element("annotations")

    track = ET.SubElement(annotation, "track", attrib={"id":"0", "label":"merged"})
    
    for frame, xtl, ytl, xbr, ybr, label, keyframe, outside, occluded, z_order in bboxes:
        box = ET.SubElement(track, "box", {
            "frame": str(frame),
            "keyframe": keyframe,
            "outside": outside,
            "occluded": occluded,
            "xtl": f"{xtl:.2f}",
            "ytl": f"{ytl:.2f}",
            "xbr": f"{xbr:.2f}",
            "ybr": f"{ybr:.2f}",
            "z_order": z_order,
            "label": label
        })

    tree = ET.ElementTree(annotation)
    output_file = os.path.join(annotation_path, f"frame_{frame_number}.xml")
    tree.write(output_file)
    print(f"Saved bounding boxes to {output_file}")


# Load bounding boxes
bboxes = parse_bboxes(xml_path)

# Process all images in compressed_frames
for filename in os.listdir(compressed_frames_path):
    compressed_image_path = os.path.join(compressed_frames_path, filename)

    # Read compressed image
    compressed_img = cv2.imread(compressed_image_path)
    new_height, new_width = compressed_img.shape[:2]

    # Extract frame number
    frame_number = get_frame_number(filename)
    if frame_number is None:
        print(f"Skipping {filename} (Could not determine frame number)")
        continue

    # Original dimensions (before cropping)
    original_width, original_height = 720, 1280  # Change if needed
    cropped_height = original_height - 560  # 280px removed from top and bottom

    # Scaling factors
    scale_x = new_width / original_width
    scale_y = new_height / cropped_height

    # Adjust bounding boxes
    scaled_bboxes = scale_bboxes(bboxes, scale_x, scale_y, 280, frame_number)

    # Draw bounding boxes
    processed_img = draw_bboxes(compressed_img, scaled_bboxes)

    # Save processed image
    output_filepath = os.path.join(output_path, filename)
    cv2.imwrite(output_filepath, processed_img)
    print(f"Processed and saved: {output_filepath}")


    # Save bounding boxes as XML
    save_bboxes_to_xml(frame_number, scaled_bboxes, annotation_path)

print("All images and annotations processed and saved!")

