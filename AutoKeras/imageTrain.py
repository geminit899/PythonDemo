import autokeras as ak
from PIL import Image
import numpy as np

if __name__ == "__main__":
    x = []
    y = []

    for i in range(17):
        x.append(np.array(Image.open('/home/geminit/图片/dm32_1440.jpg'))[:, :, 0])
        y.append("pe")
    for i in range(17):
        x.append(np.array(Image.open('/home/geminit/图片/IMG_3146.JPG'))[:, :, 0])
        y.append("sss")

    x = np.array(x)
    y = np.array(y)

    clf = ak.ImageClassifier()
    clf.fit(x, y)
