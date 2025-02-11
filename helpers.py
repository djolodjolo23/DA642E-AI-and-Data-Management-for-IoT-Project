from PIL import Image, ImageDraw

bbox_storage = {}
def drawbbox(compressed_folder_path, frame_num, new_xtl, new_ytl, new_xbr, new_ybr):
    image_path = f'{compressed_folder_path}/frame_{frame_num}.png'

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    if frame_num not in bbox_storage:
        bbox_storage[frame_num] = []
    bbox_storage[frame_num].append([new_xtl, new_ytl, new_xbr, new_ybr])
    for bbox in bbox_storage[frame_num]:
        draw.rectangle(bbox, outline='red', width=1)
    image.save(image_path)

def fix_negative_vals(val):
    return 0 if val < 0 else val