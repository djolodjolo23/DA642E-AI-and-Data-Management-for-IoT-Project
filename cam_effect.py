import cv2
import numpy as np
from scipy.ndimage import gaussian_filter
import os

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
    height, width = image.shape[:2]
    new_width = min(width, 1600)
    new_height = min(height, 1200)
    resized = cv2.resize(image, (new_width, new_height))
    
    # Step 2: Apply color adjustments (OV2640 tends to have less saturation and a slight blue tint)
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    hsv[:,:,1] = hsv[:,:,1] * 0.85  # Reduce saturation
    
    # Adjust color balance (slight blue tint)
    result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    b, g, r = cv2.split(result)
    b = np.clip(b * 1.1, 0, 255).astype(np.uint8)  # Boost blue channel
    r = np.clip(r * 0.9, 0, 255).astype(np.uint8)  # Reduce red channel
    result = cv2.merge([b, g, r])
    
    # Step 3: Reduce dynamic range (ESP32CAM has limited dynamic range)
    result = result.astype(np.float32)
    result = np.clip(result * 0.8 + 30, 0, 255).astype(np.uint8)
    
    # Step 4: Add slight lens distortion
    height, width = result.shape[:2]
    distCoeff = np.zeros((4,1), np.float64)
    # Positive k1 - barrel distortion
    distCoeff[0,0] = 0.05
    
    # Get optimal camera matrix
    camera_matrix = np.eye(3, dtype=np.float32)
    camera_matrix[0,2] = width/2
    camera_matrix[1,2] = height/2
    camera_matrix[0,0] = camera_matrix[1,1] = width
    
    # Apply distortion
    result = cv2.undistort(result, camera_matrix, distCoeff)
    
    # Step 5: Add noise (typical for low-cost sensors)
    noise = np.random.normal(0, 3, result.shape).astype(np.int)
    result = np.clip(result + noise, 0, 255).astype(np.uint8)
    
    # Step 6: Add some blur (OV2640 isn't the sharpest)
    result = cv2.GaussianBlur(result, (3, 3), 0.5)
    
    # Step 7: Add JPEG compression artifacts
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
    _, buffer = cv2.imencode(".jpg", result, encode_param)
    result = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    
    # Save or show the result
    if output_path:
        cv2.imwrite(output_path, result)
        print(f"Processed image saved to {output_path}")
    
    return result

def create_comparison(original_path, output_path):
    """
    Create a side-by-side comparison of original and processed images.
    
    Args:
        original_path (str): Path to the original image.
        output_path (str): Path to save the comparison image.
    """
    original = cv2.imread(original_path)
    processed = apply_ov2640_effect(original_path)
    
    # Resize if needed to make same height
    h1, w1 = original.shape[:2]
    h2, w2 = processed.shape[:2]
    
    if h1 != h2:
        # Resize to match heights
        aspect_ratio = w1 / h1
        new_h = min(h1, h2)
        new_w = int(new_h * aspect_ratio)
        original = cv2.resize(original, (new_w, new_h))
    
    # Create side-by-side comparison
    comparison = np.hstack((original, processed))
    
    # Add labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(comparison, "Original", (10, 30), font, 1, (0, 255, 0), 2)
    cv2.putText(comparison, "OV2640 Effect", (original.shape[1] + 10, 30), font, 1, (0, 255, 0), 2)
    
    cv2.imwrite(output_path, comparison)
    print(f"Comparison image saved to {output_path}")

# Example usage
if __name__ == "__main__":
    # Apply effect to a single image
    apply_ov2640_effect("high_quality_image.jpg", "ov2640_effect.jpg")
    
    # Create comparison
    create_comparison("high_quality_image.jpg", "comparison.jpg")