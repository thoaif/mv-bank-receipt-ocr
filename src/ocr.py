import copy
from typing import Tuple, List, Iterable, Union

from PIL import Image
import pytesseract
import cv2
import numpy as np

FIELDS = ['Status', 'Message', 'Ref #', 'Date', 'From', 'To', 'Amount', 'Remarks']

WIDTH = 500


def random_color() -> Tuple[int, int, int]:
    """
    get a random color
    """
    return tuple(np.random.randint(0, 256, (3,), dtype=np.uint8).tolist())


def get_rows(image: np.ndarray) -> List[np.ndarray]:
    """
    returns row as image segments
    """
    padding = 4
    h, w = image.shape

    # convert to binary color
    img_thresholded = cv2.threshold(image, 250, 255, cv2.THRESH_BINARY_INV)[1]

    # horizontal filter, the length is same as the image
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w, 1))

    # keep only horizontal features
    image_2 = cv2.erode(img_thresholded, hor_kernel, iterations=3)
    horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)

    # invert colors
    inverted = cv2.threshold(horizontal_lines, 100, 255, cv2.THRESH_BINARY_INV)[1]

    # add some padding to make sure boxes are captured in the next step
    cv2.rectangle(inverted, (0, 0), (w, h), (0, 0, 0), padding)

    # get the contours of the boxes
    contours, hierarchy = cv2.findContours(inverted, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # convert contours to their bounding boxes. rectangles in (x1, y1, w, h) format
    rectangles = [cv2.boundingRect(contour) for contour in contours]

    # filter out boxes that don't meed a minimum height. Also keep it in (x1, y1, x2, y2) format
    min_height = h * 0.05
    rectangles = [(x, y, x + w, y + h) for (x, y, w, h) in rectangles if h >= min_height]

    # uncomment below to visualize:
    # cv2.imshow('img_thresholded', img_thresholded)
    # cv2.imshow('horizontal_lines', horizontal_lines)
    # cv2.imshow('inverted', inverted)
    #
    # extracted_boxes = np.ones((h, w, 3), dtype=np.uint8) * 255
    # for (x1, y1, x2, y2) in rectangles:
    #     cv2.rectangle(extracted_boxes, (x1, y1), (x2, y2), random_color(), 4)
    #
    # cv2.imshow('extracted_boxes', extracted_boxes)
    # cv2.waitKey()

    # sort by descending y position
    rectangles.sort(key=lambda rect: rect[1])

    # gets rid of the unnecessary last row
    rectangles = rectangles[:-1]

    # convert to image segments
    rows = [image[y1: y2, x1: x2] for (x1, y1, x2, y2) in rectangles]

    return rows


def find_target(targets: Iterable, line: str) -> Union[None, str]:
    """
    tries to find a target from a list of targets
    """
    gen = (item for item in targets if item in line)
    return next(gen, None)


def scale_by_width(image: np.ndarray, width: int) -> np.ndarray:
    """
    scale image while keeping the aspect ratio
    """
    height_, width_ = image.shape[:2]
    ratio = height_ / width_
    new_height = round(ratio * width)
    return cv2.resize(image, (width, new_height))


def clear_lines(line: str):
    new_line = line.split('\n')
    return ' '.join(new_line)


def remove_and_strip(field: str, line: str) -> str:
    new_line = line[len(field):].strip()
    return new_line


def process_amount(predictions, field: str, line: str):
    amount = remove_and_strip(field, line)
    if ' ' not in line:
        predictions[field] = amount
    else:
        splits = amount.split(' ', 1)
        predictions['Currency'] = splits[0].strip()
        predictions[field] = splits[1].strip()


def process_to(predictions: dict, field: str, line: str):
    to = remove_and_strip(field, line)
    if '\n' in to:
        splits = to.split('\n', 1)
        predictions[field] = {'Name': splits[0].strip(), 'Account': splits[1].strip()}
    else:
        if to.isnumeric() or 'XXXX' in to:
            predictions[field] = {'Account': to}
        else:
            predictions[field] = {'Name': to}


def process_normal(predictions: dict, field: str, line: str):
    value = remove_and_strip(field, line)
    value = clear_lines(value)
    predictions[field] = value


def find_field(fields: Iterable, string: str):
    generator = (field for field in fields if string.startswith(field))
    return next(generator, None)


processing_map = {f: process_normal for f in FIELDS}
processing_map['Amount'] = process_amount
processing_map['To'] = process_to


def predict(image: np.ndarray) -> dict:
    """
    main function for predicting
    """

    # standardize the width
    image = scale_by_width(image, WIDTH)

    # convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # get row segments
    rows = get_rows(image)

    predictions = {}
    remaining_fields = copy.copy(FIELDS)

    for row in rows:
        # predict row text
        text = pytesseract.image_to_string(Image.fromarray(row)).strip()
        text = text.strip()
        field = find_field(remaining_fields, text)
        if field is not None:
            processing_map[field](predictions, field, text)
            remaining_fields.remove(field)

    return predictions


def run_ocr(image_path: str) -> dict:
    image = cv2.imread(str(image_path))
    return predict(image)
