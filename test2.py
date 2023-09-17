from ai.util.img_reader_util import (
    find_image,
    find_all_images,
    non_max_suppression,
)
import numpy as np
import os
import pyautogui
import cv2
import time

needle_image = cv2.imread("img/labyrinth/labyrinth_portal2.png")
haystack_image = cv2.imread("haystack.png")

try:
    start = time.time()
    image_locs = []
    confidence = []
    i1, c1 = find_all_images(
        needle_image, haystack_image, stop_confidence=0.85
    )
    i2, c2 = find_all_images(
        cv2.imread("img/labyrinth/labyrinth_portal1.png"),
        haystack_image,
        stop_confidence=0.85,
    )
    i3, c3 = find_all_images(
        cv2.imread("img/labyrinth/labyrinth_portal3.png"),
        haystack_image,
        stop_confidence=0.85,
    )
    i4, c4 = find_all_images(
        cv2.imread("img/labyrinth/labyrinth_portal4.png"),
        haystack_image,
        stop_confidence=0.85,
    )
    #
    # combine all the image_locs, image_locs is a (5,4) array
    # also keep in mind that i2, i3, i4 might be empty
    if i1.count != 0:
        print(i1)
        print(image_locs)
        image_locs += i1
        # print shape of c1
        print(c1)
        print(confidence)
        confidence += c1
    if i2.count != 0:
        image_locs += i2
        confidence += c2
    if i3.count != 0:
        image_locs += i3
        confidence += c3
    if i4.count != 0:
        image_locs += i4
        confidence += c4

    # add confidence as a column to image_locs
    image_locs = np.c_[image_locs, confidence]

    # remove overlapping bounding boxes using non-max suppression
    # print(image_locs.shape)
    boxes, confidences = non_max_suppression(image_locs, 0)
    # print(boxes.shape)

    image_locs = boxes
    # print image_loc and confidence
    print(image_locs)
    print(confidence)

    # draw a rectangle around the image, each loc is x, y, w, h
    blank = np.zeros(
        (haystack_image.shape[0], haystack_image.shape[1], 3), np.uint8
    )
    for image_loc in image_locs:
        cv2.rectangle(
            blank,
            (image_loc[0], image_loc[1]),
            (
                image_loc[0] + image_loc[2],
                image_loc[1] + image_loc[3],
            ),
            (0, 255, 0),
            2,
        )
    end = time.time()
    print("Time elapsed: " + str(end - start))

    # show the image
    final = cv2.addWeighted(haystack_image, 0.8, blank, 1, 0)
    cv2.imshow("image", final)
    cv2.waitKey(0)
except RuntimeError:
    print("Image not found")
