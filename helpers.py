from PIL import Image, ImageDraw

bbox_storage = {}
def drawbbox(compressed_folder_path, file_name, new_xtl, new_ytl, new_xbr, new_ybr):
    image_path = f'{compressed_folder_path}/{file_name}'

    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    if file_name not in bbox_storage:
        bbox_storage[file_name] = []
    bbox_storage[file_name].append([new_xtl, new_ytl, new_xbr, new_ybr])
    for bbox in bbox_storage[file_name]:
        draw.rectangle(bbox, outline='red', width=1)
    image.save(image_path)

def fix_negative_vals(val):
    return 0 if val < 0 else val