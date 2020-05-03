import copy

from PIL import Image
import pytesseract
import cv2
import numpy as np

from src.ocr.preprocessing import contrast_brightness, get_rows, standardize, min_max_standardize
from src.ocr.text_processing import FIELDS, find_field, processing_map


def predict(image: np.ndarray) -> dict:
    """
    main function for predicting
    """
    image = standardize(image)
    height_, width_ = image.shape[:2]
    print('{} {}'.format(width_, height_))

    # get row segments
    rows = get_rows(image)

    predictions = {}
    remaining_fields = copy.copy(FIELDS)

    for row in rows:
        # apply some filtering to the row
        row = contrast_brightness(row)
        row = min_max_standardize(row)

        # predict text
        text = pytesseract.image_to_string(Image.fromarray(row)).strip()
        text = text.strip()

        field = find_field(remaining_fields, text)
        if field is not None:

            # apply text processing
            processing_map[field](predictions, field, text)
            remaining_fields.remove(field)

    return predictions


def run_ocr(image_path: str) -> dict:
    image = cv2.imread(str(image_path))
    return predict(image)
