import os
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

def apply_ov2640_effect(image_path, output_path=None):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")

    # Reduced saturation - budget CMOS sensors typically have less vivid color reproduction
    # Color tint - the OV2640 often shows a slight blue tint due to its color processing and white balance limitations, especially under certain lighting conditions
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = hsv[:, :, 1] * 0.85  # Reduce saturation
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b, g, r = cv2.split(result)
    b = np.clip(b * 1.1, 0, 255).astype(np.uint8)  # Boost blue channel
    r = np.clip(r * 0.9, 0, 255).astype(np.uint8)  # Reduce red channel
    result = cv2.merge([b, g, r])

    # This code compresses the contrast and lifts shadows, simulating how the OV2640 struggles with high-contrast scenes, 
    # often producing images where shadows appear more grey than black.
    result = result.astype(np.float32)
    result = np.clip(result * 0.8 + 30, 0, 255).astype(np.uint8)

    # The inexpensive lenses typically paired with OV2640 sensors in modules like the ESP32CAM exhibit barrel distortion,
    # where straight lines bow outward from the center. The distortion coefficient of 0.05 adds a subtle barrel effect to simulate this optical characteristic
    height, width = result.shape[:2]
    dist_coeff = np.zeros((4, 1), np.float64)
    dist_coeff[0, 0] = 0.05  # Barrel distortion
    
    camera_matrix = np.eye(3, dtype=np.float32)
    camera_matrix[0, 2] = width / 2
    camera_matrix[1, 2] = height / 2
    camera_matrix[0, 0] = camera_matrix[1, 1] = width
    result = cv2.undistort(result, camera_matrix, dist_coeff)

    # The standard deviation of 3 adds Gaussian noise to simulate the electronic noise characteristics of 
    # this lower-cost CMOS sensor, which has a lower signal-to-noise ratio compared to premium sensors.
    noise = np.random.normal(0, 3, result.shape).astype(int)
    result = np.clip(result + noise, 0, 255).astype(np.uint8)

    # The limited resolving power of inexpensive lenses used with OV2640
    #The in-camera processing that often applies noise reduction which reduces detail
    result = cv2.GaussianBlur(result, (3, 3), 0.5)

    # JPEG compression
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    _, buffer = cv2.imencode(".jpg", result, encode_param)
    result = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    
    if output_path:
        cv2.imwrite(output_path, result)
        print(f"Processed image saved to {output_path}")
    
    return result

input_folder = "augmented/fruits.mp4/images"
output_folder = "compressed_augmented_and_processed/fruits/frames_128 x 128"

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)
        apply_ov2640_effect(input_file_path, output_file_path)
