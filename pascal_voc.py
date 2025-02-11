import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def write_pascal_voc(file_path, filename, label, width, height, xtl, ytl, xbr, ybr):
    with open(file_path, 'w') as file:
        xml_content = f'''<annotation>
          <folder>frame</folder>
          <filename>{filename}</filename>
          <source>
            <database>Unknown</database>
            <annotation>Unknown</annotation>
            <image>Unknown</image>
          </source>
          <size>
            <width>{width}</width>
            <height>{height}</height>
            <depth></depth>
          </size>
          <segmented>0</segmented>
          <object>
            <name>{label}</name>
            <truncated>0</truncated>
            <occluded>0</occluded>
            <difficult>0</difficult>
            <bndbox>
              <xmin>{xtl}</xmin>
              <ymin>{ytl}</ymin>
              <xmax>{xbr}</xmax>
              <ymax>{ybr}</ymax>
            </bndbox>
          </object>
        </annotation>'''
        file.write(xml_content)


def append_object_to_pascal_voc(file_path, label, xtl, ytl, xbr, ybr):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        obj = ET.Element("object")

        name = ET.SubElement(obj, "name")
        name.text = label

        truncated = ET.SubElement(obj, "truncated")
        truncated.text = "0"

        occluded = ET.SubElement(obj, "occluded")
        occluded.text = "0"

        difficult = ET.SubElement(obj, "difficult")
        difficult.text = "0"

        bndbox = ET.SubElement(obj, "bndbox")

        xmin = ET.SubElement(bndbox, "xmin")
        xmin.text = str(float(xtl))

        ymin = ET.SubElement(bndbox, "ymin")
        ymin.text = str(float(ytl))

        xmax = ET.SubElement(bndbox, "xmax")
        xmax.text = str(float(xbr))

        ymax = ET.SubElement(bndbox, "ymax")
        ymax.text = str(float(ybr))

        root.append(obj)

        rough_string = ET.tostring(root, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        cleaned_xml = "\n".join([line for line in pretty_xml.split("\n") if line.strip()])

        with open(file_path, "w") as f:
            f.write(cleaned_xml)
        print(f"Appended new object '{label}' to {file_path}")

    except Exception as e:
        print(f"Error updating XML: {e}")
