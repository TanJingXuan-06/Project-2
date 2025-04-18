print("This is Project 1")


import cv2
import numpy as np
import os

# ASCII characters used to build the output text
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100):
    height, width = image.shape
    ratio = height / width
    new_height = int(new_width * ratio * 0.55)  # 0.55 makes aspect ratio better
    return cv2.resize(image, (new_width, new_height))

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def pixels_to_ascii(image):
    ascii_str = ""
    for row in image:
        for pixel in row:
            ascii_str += ASCII_CHARS[pixel // 25]
        ascii_str += "\n"
    return ascii_str

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = grayscale(frame)
        small_gray = resize_image(gray, new_width=120)
        ascii_art = pixels_to_ascii(small_gray)

        os.system('cls' if os.name == 'nt' else 'clear')  # clear terminal
        print(ascii_art)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    pass

cap.release()
cv2.destroyAllWindows()
