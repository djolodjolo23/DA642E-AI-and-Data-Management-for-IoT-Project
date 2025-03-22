# README

## Script Overview

### `frame_extractor.py`
This script takes a video and a CVAT annotation file as input and extracts individual frames from the videos based on the annotation file. It loops through the XML tree, checks which frames are annotated, and extracts these frames to the appropriate folder.

### `remove_frames.py`
Since videos were recorded at 30 frames per second, many frames appeared very similar, which could lead to overfitting during training. This script discards 3 out of every 4 sequential frames, leaving only ¼ of the original training data.

### `compress_generate.py`
This script converts input images to square output images using a fit-shortest-axis style, cropping the longer axis to form a square before resizing to the appropriate resolution. It was used to scale full-HD images to either **96×96** or **128×128** for model training. Additionally, the script recalculates bounding box information and creates a new `.xml` annotation file in Pascal VOC format.

### `augmentation.py`
To increase dataset variety and reduce overfitting, this script applies random augmentations such as flipping, rotation, and zooming. Three augmented copies of each frame are generated, each with unique parameters. A hash value is assigned to ensure no augmented copy is identical.

### `cam_effect.py`
This script simulates the characteristics of an **ESP32-CAM** onboard camera by applying various image degradations:
- **Color adjustment**: Reduced saturation and slight blue tint to mimic OV2640 sensor's color reproduction.
- **Dynamic range reduction**: Contrast compression and shadow lifting to simulate weak contrast handling.
- **Lens distortion simulation**: Small barrel distortion to match the ESP32-CAM lens imperfections.
- **Noise injection**: Gaussian noise to replicate the high noise levels of low-cost CMOS sensors.
- **Blurring**: Slight blur to mimic reduced resolving power of the OV2640 lens.
- **JPEG compression artifacts**: Re-encoding at 80% quality to match the ESP32-CAM’s built-in JPEG compression.


### `annotate_testing_frames.py`
This script processes test images similarly to `compress_generate.py` but with adjustments for differences in annotation file formats. CVAT generates different annotations for videos versus images, so the script properly loops through image metadata, compresses and crops (if needed), recalculates bounding boxes, and generates annotation files.