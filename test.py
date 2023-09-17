from ai.util.img_reader_util import find_image
from ai.util.img_reader_util import find_all_images
import numpy as np
import os
import pyautogui
import cv2
import time

needle_image = cv2.imread("img/labyrinth/decrease_as.png")
haystack_image = cv2.imread("haystack.png")

try:
    # haystack_image = haystack_image[700:]
    start = time.time()
    loc, confidence = find_image(
        needle_image,
        haystack_image,
        start_confidence=1,
        stop_confidence=0.8,
    )
    if not loc:
        raise RuntimeError
    # print image_loc and confidence
    print(loc)
    print(confidence)

    # draw a rectangle around the image, loc is x, y, w, h
    blank = np.zeros(
        (haystack_image.shape[0], haystack_image.shape[1], 3), np.uint8
    )
    cv2.rectangle(
        blank,
        (loc[0], loc[1]),
        (loc[0] + loc[2], loc[1] + loc[3]),
        (0, 255, 0),
        2,
    )

    # draw a dot in the center of the image
    coords = pyautogui.center(loc)
    print(coords)
    cv2.circle(
        blank,
        (coords.x, coords.y),
        5,
        (0, 0, 255),
        -1,
    )
    pyautogui.click(coords.x, coords.y)

    end = time.time()
    print("Time elapsed: " + str(end - start))

    # show the image
    final = cv2.addWeighted(haystack_image, 0.8, blank, 1, 0)
    cv2.imshow("image", final)
    cv2.waitKey(0)
except RuntimeError:
    print("Image not found")
