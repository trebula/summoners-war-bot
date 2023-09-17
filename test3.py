import io
import logging
import pyautogui
from google.cloud import vision_v1 as vision
from google.api_core.exceptions import GoogleAPICallError, RetryError


class VisionClient:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = (
                vision.ImageAnnotatorClient.from_service_account_json(
                    "summoners-war-ocr.json.key"
                )
            )
        return cls._client


def click_all_words(word: str, haystack_image=None):
    """Clicks all occurrences of the word on the screen."""
    try:
        if haystack_image is None:
            haystack_image = pyautogui.screenshot()

        # load image
        byte_stream = io.BytesIO()
        haystack_image.save(byte_stream, format="PNG")
        image_bytes = byte_stream.getvalue()
        image = vision.Image(content=image_bytes)

        # detect text in the image
        logging.info("Using Google Vision API to detect text in image...")
        response = VisionClient.get_client().text_detection(image=image)  # type: ignore
        logging.info("Detected text in image.")
        texts = response.text_annotations

        for text in texts[1:]:
            if word.lower() in text.description.lower():
                # extract vertices of the bounding polygon
                vertices = [
                    (vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices
                ]
                # calculate the center of the bounding box
                center_x = (vertices[0][0] + vertices[2][0]) // 2
                center_y = (vertices[0][1] + vertices[2][1]) // 2
                # click on the center of the bounding box
                # halve the coordinates because mac retina display
                pyautogui.click(center_x // 2, center_y // 2)
    except (GoogleAPICallError, RetryError, ValueError) as e:
        logging.error(f"An error occurred: {e}")
