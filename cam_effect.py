import os
import cv2
import numpy as np
from scipy.ndimage import gaussian_filter

def apply_ov2640_effect(image_path, output_path=None):
    """
    Apply OV2640 camera effect to a high-quality image.
    
    Args:
        image_path (str): Path to the original high-quality image.
        output_path (str, optional): Path to save the processed image. If None, the result is shown but not saved.
    
    Returns:
        numpy.ndarray: The processed image with OV2640 effect applied.
    """
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Step 1: Resize to typical OV2640 resolution
    # OV2640 Relation: The OV2640 has a maximum resolution of 1600×1200 pixels (UXGA). 
    # This limitation is hardware-based - the sensor physically has this number of pixels. 
    # Your code ensures that images don't exceed this resolution, which is accurate to the sensor's capabilities.
    height, width = image.shape[:2]
    new_width = min(width, 1600)
    new_height = min(height, 1200)
    resized = cv2.resize(image, (new_width, new_height))
    
    # Step 2: Apply color adjustments (less saturation and a slight blue tint)
    # OV2640 Relation: This mimics two characteristics of the OV2640:

    # OV2640 Relation: This mimics two characteristics of the OV2640:

    # Reduced saturation - budget CMOS sensors typically have less vivid color reproduction
    # Color tint - the OV2640 often shows a slight blue tint due to its color processing and white balance limitations, especially under certain lighting conditions
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = hsv[:, :, 1] * 0.85  # Reduce saturation
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b, g, r = cv2.split(result)
    b = np.clip(b * 1.1, 0, 255).astype(np.uint8)  # Boost blue channel
    r = np.clip(r * 0.9, 0, 255).astype(np.uint8)  # Reduce red channel
    result = cv2.merge([b, g, r])
    
    # Step 3: Reduce dynamic range
    # OV2640 Relation: The OV2640 has a more limited dynamic range (around 60-70dB) compared to high-end cameras. 
    # This code compresses the contrast and lifts shadows, simulating how the OV2640 struggles with high-contrast scenes, 
    # often producing images where shadows appear more grey than black.
    result = result.astype(np.float32)
    result = np.clip(result * 0.8 + 30, 0, 255).astype(np.uint8)
    
    # Step 4: Add slight lens distortion
    # OV2640 Relation: The inexpensive lenses typically paired with OV2640 sensors in modules like the ESP32CAM exhibit barrel distortion, 
    # where straight lines bow outward from the center. The distortion coefficient of 0.05 adds a subtle barrel effect to simulate this optical characteristic
    height, width = result.shape[:2]
    distCoeff = np.zeros((4, 1), np.float64)
    distCoeff[0, 0] = 0.05  # Barrel distortion
    
    camera_matrix = np.eye(3, dtype=np.float32)
    camera_matrix[0, 2] = width / 2
    camera_matrix[1, 2] = height / 2
    camera_matrix[0, 0] = camera_matrix[1, 1] = width
    result = cv2.undistort(result, camera_matrix, distCoeff)
    
    # Step 5: Add noise (typical for low-cost sensors)
    # OV2640 Relation: The OV2640 has relatively high noise levels, especially in low light. 
    # The standard deviation of 3 adds Gaussian noise to simulate the electronic noise characteristics of 
    # this lower-cost CMOS sensor, which has a lower signal-to-noise ratio compared to premium sensors.
    noise = np.random.normal(0, 3, result.shape).astype(int)
    result = np.clip(result + noise, 0, 255).astype(np.uint8)
    
    # Step 6: Add some blur (OV2640 isn’t the sharpest)
    # OV2640 Relation: This simulates two factors:

    # The limited resolving power of inexpensive lenses used with OV2640
    #The in-camera processing that often applies noise reduction which reduces detail
    result = cv2.GaussianBlur(result, (3, 3), 0.5)
    
    # Step 7: Add JPEG compression artifacts
    # OV2640 Relation: The ESP32CAM typically uses JPEG compression to store images due to memory constraints. 
    # The quality setting of 80 introduces compression artifacts similar to what you'd see 
    # from the hardware-accelerated JPEG encoder in the ESP32CAM.
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    _, buffer = cv2.imencode(".jpg", result, encode_param)
    result = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    
    # Save or show the result
    if output_path:
        cv2.imwrite(output_path, result)
        print(f"Processed image saved to {output_path}")
    
    return result

# Define the input folder containing the original images
input_folder = "compressed/fruits.mp4/frames_128 x 128"

# Define the output folder where processed images will be stored
output_folder = "compressed_and_processed/frames_128 x 128"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through each file in the input folder and process images
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)
        apply_ov2640_effect(input_file_path, output_file_path)
