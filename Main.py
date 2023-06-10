import pytesseract as tess
from PIL import Image
import cv2

tess.pytesseract.tesseract_cmd = r'<insert path to tesseract executable here>'

image = Image.open(r'<insert path to image here>')
imageText = tess.image_to_string(image)

print(imageText)
