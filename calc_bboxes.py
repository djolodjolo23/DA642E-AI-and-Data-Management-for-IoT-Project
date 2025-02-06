import cv2
import xml.etree.ElementTree as ET

# File paths (update these if necessary)
xml_path = "output.xml"
original_image_path = "frames/fruits.mp4/frame_0.png"
compressed_image_path = "frames/fruits.mp4/frame_0_compressed.jpg"

"""# Original and new dimensions
original_width, original_height = 720, 1080
new_width, new_height = 200, 200

"""

# Read original image and get its dimensions
original_img = cv2.imread(original_image_path)
original_height, original_width = original_img.shape[:2]

# Read compressed image and get its dimensions
compressed_img = cv2.imread(compressed_image_path)
new_height, new_width = compressed_img.shape[:2]

#print("Original image size: ", original_height, original_width, "Compressed image size: ", new_height, new_width)

# Scaling factors
scale_x = new_width / original_width
scale_y = new_height / original_height

# Function to load and parse bounding boxes from XML
def parse_bboxes(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    bboxes = []
    
    for box in root.findall(".//box"):  # Find all <box> elements
        frame = int(box.get("frame"))  # Frame number
        xtl = float(box.get("xtl"))
        ytl = float(box.get("ytl"))
        xbr = float(box.get("xbr"))
        ybr = float(box.get("ybr"))
        label = box.get("label")

        bboxes.append((frame, xtl, ytl, xbr, ybr, label))
    
    return bboxes


bboxes = parse_bboxes("output.xml")
#print("Extracted Bounding Boxes:", bboxes)
#print(" ")


def scale_bboxes(bboxes, scale_x, scale_y):
    scaled_bboxes = []
    for frame, xtl, ytl, xbr, ybr, label in bboxes:
        xtl_new = round(xtl * scale_x)
        ytl_new = round(ytl * scale_y)
        xbr_new = round(xbr * scale_x)
        ybr_new = round(ybr * scale_y)
        scaled_bboxes.append((frame, xtl_new, ytl_new, xbr_new, ybr_new, label))
    
    return scaled_bboxes



scaled_bboxes = scale_bboxes(bboxes, scale_x, scale_y)
#print("Scaled Bounding Boxes:", scaled_bboxes)
#print(" ")


def draw_bboxes(image, bboxes, target_frame=0):
    for frame, xtl, ytl, xbr, ybr, label in bboxes:
        if frame != target_frame:
            continue  # Skip bounding boxes from other frames
        
        color = (0, 255, 0)  # Green box
        thickness = 1
        cv2.rectangle(image, (xtl, ytl), (xbr, ybr), color, thickness)

    return image


compressed_img = cv2.imread(compressed_image_path)
compressed_img_with_bboxes = draw_bboxes(compressed_img, scaled_bboxes)

print(f"Original Size: {original_width}x{original_height}")
print(f"Compressed Size: {new_width}x{new_height}")
print(f"Scaling Factors: {scale_x}, {scale_y}")
for bbox in scaled_bboxes:
    print(f"Rescaled Bounding Box: {bbox}")

cv2.imshow("Bounding Boxes", compressed_img_with_bboxes)
cv2.waitKey(0)
cv2.destroyAllWindows()
