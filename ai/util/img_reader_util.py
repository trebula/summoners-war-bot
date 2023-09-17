import cv2
import numpy as np
import os
import pyautogui
import typing


# implementation of Non-Maximum Suppression
# https://pyimagesearch.com/2015/02/16/faster-non-maximum-suppression-python/
def non_max_suppression(boxes, overlapThresh) -> tuple[list, list]:
    """
    Non-max suppression

    Args:
        boxes (np.ndarray): The boxes to suppress
        overlapThresh (float): The overlap threshold

    Returns:
        (np.ndarray): The suppressed boxes
        (np.ndarray): The confidence values of the suppressed boxes
    """
    # convert (x, y, w, h, confidence) to (x1, y1, x2, y2, confidence)
    boxes = np.array(
        [
            (loc[0], loc[1], loc[0] + loc[2], loc[1] + loc[3], loc[4])
            for loc in boxes
        ]
    )

    # if there are no boxes, return an empty list
    if len(boxes) == 0:
        return [], []

    # if the bounding boxes integers, convert them to floats --
    # this is important since we'll be doing a bunch of divisions
    if boxes.dtype.kind == "i":
        boxes = boxes.astype("float")

    # initialize the list of picked indexes
    pick = []

    # grab the coordinates of the bounding boxes
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(y2)

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        # compute the ratio of overlap
        overlap = (w * h) / area[idxs[:last]]

        # delete all indexes from the index list that have overlap greater than the threshold
        idxs = np.delete(
            idxs,
            np.concatenate(([last], np.where(overlap > overlapThresh)[0])),
        )

    # if confidences available, also return the confidences
    confidences = []
    if boxes.shape[1] > 4:
        confidences = boxes[pick, 4]
        # remove the confidences from the boxes
        boxes = boxes[pick, :4]

    # return only the bounding boxes that were picked
    # convert (x1, y1, x2, y2) to (x1, y1, w, h)
    boxes = boxes.astype("int")
    boxes = np.array(
        [(loc[0], loc[1], loc[2] - loc[0], loc[3] - loc[1]) for loc in boxes]
    )

    # flip confidences to match boxes
    confidences = np.flip(confidences)
    return boxes.tolist(), confidences.tolist()


def find_image(
    needle_image,
    haystack_image=None,
    grayscale=False,
    start_confidence=0.9,
    stop_confidence=0.55,
    maximize_confidence=False,
    scales=[],
) -> tuple[typing.Any, float]:
    """
    Finds a single occurence of the needle image in a haystack image.
    Returns None, None if not found

    Args:
        needle_image (np.ndarray): The image to find
        haystack_image (np.ndarray): The image to search in
        grayscale (bool): Convert the images to grayscale for faster processing?
        start_confidence (float): The maximum confidence of the match
        stop_confidence (float): The minimum confidence of the match
        maximize_confidence (bool): Search for highest confidence match?
        scales (bool): The scales to search for the image

    Returns:
        (tuple): The x, y, w, h of the match
        (float): The confidence of the match
    """

    # if no haystack image is given, use current screen
    if haystack_image is None:
        haystack_image = pyautogui.screenshot()
        # save screenshot for debugging
        haystack_image.save("haystack.png")

    # Returns location of needle image and confidence value
    scaled_needle_image = needle_image  # scaled starts at 100%

    def locate_needle_image():
        """Helper function to locate needle image.

        Returns:
            (tuple): The x, y, w, h of the match or None if not found
            (float): The confidence of the match or 0 if not found
        """
        image_loc = None
        confidence = start_confidence

        while confidence > stop_confidence:
            # find the image
            image_loc = pyautogui.locate(
                scaled_needle_image,
                haystack_image,
                grayscale=grayscale,
                confidence=confidence,
            )

            if image_loc is not None:
                return image_loc, confidence
            # if not found, lower confidence
            else:
                confidence -= 0.05
        # image not found
        return [], 0

    image_loc, confidence = locate_needle_image()

    # image found and not maximizing confidence
    if image_loc and (
        not maximize_confidence or confidence == start_confidence or not scales
    ):
        return image_loc, confidence

    # init variables for maximize_confidence setting
    best_image_loc = None
    highest_confidence = stop_confidence

    for scale in scales:
        scaled_needle_image = cv2.resize(
            needle_image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )

        image_loc, confidence = locate_needle_image()

        if image_loc:
            if not maximize_confidence or confidence == start_confidence:
                return image_loc, confidence
            elif confidence > highest_confidence:
                highest_confidence = confidence
                best_image_loc = image_loc
            # maximizing confidence and image found with lower confidence
            else:
                # because scales are sorted,
                # if confidence <= highest_confidence, we know we can stop
                return best_image_loc, highest_confidence

    # if no image found, return empty
    return [], 0


def find_all_images(
    needle_image,
    haystack_image=None,
    grayscale=False,
    start_confidence=0.9,
    stop_confidence=0.65,
    scales=[],
) -> tuple[list, list]:
    """
    Finds all occurences of the needle image in a haystack image.
    Returns None, None if not found

    Args:
        needle_image (np.ndarray): The image to find
        haystack_image (np.ndarray): The image to search in
        grayscale (bool): Convert the images to grayscale for faster processing?
        start_confidence (float): The maximum confidence of the match
        stop_confidence (float): The minimum confidence of the match
        scales (list): The scales to search for the image

    Returns:
        (list): List of tuples (x1, y1, x2, y2) of all matches
        (list): List of all confidences of the matches
    """

    # if no haystack image is given, use current screen
    if haystack_image is None:
        haystack_image = pyautogui.screenshot()

    # Returns locations of needle images and confidence values
    image_locs = []
    scaled_needle_image = needle_image  # scaled starts at 100%

    def locate_all_needle_images():
        image_loc = None
        confidence = start_confidence

        while confidence > stop_confidence:
            # find the image
            image_loc = pyautogui.locateAll(
                scaled_needle_image,
                haystack_image,
                grayscale=grayscale,
                confidence=confidence,
            )

            # append image locations and confidence
            for loc in image_loc:
                image_locs.append((loc[0], loc[1], loc[2], loc[3], confidence))
            confidence -= 0.1

    def remove_overlap(image_locs):
        # remove overlapping bounding boxes using non-max suppression
        boxes, confidences = non_max_suppression(image_locs, 0.5)
        return boxes, confidences

    locate_all_needle_images()

    # rescale the needle image
    for scale in scales:
        scaled_needle_image = cv2.resize(
            needle_image,
            None,
            fx=scale,
            fy=scale,
            interpolation=cv2.INTER_CUBIC,
        )
        locate_all_needle_images()

    return remove_overlap(image_locs)
