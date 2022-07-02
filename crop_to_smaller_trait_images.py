import os
from PIL import Image

for name in os.listdir("img"):
    filepath = os.path.join("img", name)
    if not os.path.isfile(filepath):
        continue

    cropped_filepath = os.path.join("img", "small", name)
    print(name)

    img = Image.open(filepath)
    area = (476 - 102, 0, 476 - 4, 94)
    cropped_img = img.crop(area)
    cropped_img.save(cropped_filepath)
    print(cropped_filepath)
