from typing import List, Tuple

import cv2
import numpy as np

from src.ocr.preprocessing import min_max_threshold
from src.ocr.preprocessing.polygon_manipulate import get_approx_polygon, is_approx_rect, is_line

PADDING = 20


def random_color() -> Tuple[int, int, int]:
    """
    get a random color
    """
    return tuple(np.random.randint(0, 256, (3,), dtype=np.uint8).tolist())


def apply_filters(image: np.ndarray):
    """
    applies filters to highlight rows
    """

    img_h, img_w = image.shape

    # convert to binary color
    img_thresholded = cv2.threshold(image, 250, 255, cv2.THRESH_BINARY_INV)[1]

    # horizontal filter, the length is same as the image
    hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (round(img_w * 0.15), 1))

    # keep only horizontal features
    image_2 = cv2.erode(img_thresholded, hor_kernel, iterations=3)
    horizontal_lines = cv2.dilate(image_2, hor_kernel, iterations=3)

    # add some padding to make sure boxes are captured in the next step
    cv2.rectangle(horizontal_lines, (0, 0), (img_w, img_h), (0, 0, 0), PADDING)

    return horizontal_lines


def get_row_rectangles(contours: List[np.ndarray], img_shape: Tuple[int, int], max_height: float,
                       row_min_height: float):
    """
    processes contours and returns the rectangles of rows
    """
    img_h, img_w = img_shape

    # add extremes
    row_ys = {0, img_h}

    for contour in contours:
        if is_approx_rect(contour):
            # convert to a line
            contour_rect = get_approx_polygon(contour, points=2)
            x, y, w, h = cv2.boundingRect(contour_rect)

            # add to row if it is a line
            if is_line(w, h, max_height):
                row_ys.add(y)

    row_ys = list(row_ys)
    row_ys.sort()

    # create a list of rectangle rows
    rectangles = [(0, y1, img_w, y2) for y1, y2 in zip(row_ys, row_ys[1:]) if y2 - y1 > row_min_height]

    return rectangles


def get_rows(image: np.ndarray) -> List[np.ndarray]:
    """
    returns row as image segments
    """
    img_h, img_w = image.shape

    max_height = img_h * 0.01
    row_min_height = img_h * 0.01

    # line highlighting filter
    horizontal_lines = apply_filters(image)

    # get the contours of the boxes
    contours, hierarchy = cv2.findContours(horizontal_lines, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    rectangles = get_row_rectangles(contours, image.shape, max_height, row_min_height)

    # uncomment below to visualize:
    # cv2.imshow('horizontal_lines', horizontal_lines)
    # cv2.imshow('image', image)
    #
    # extracted_boxes = image.copy()
    # for (x1, y1, x2, y2) in rectangles:
    #     cv2.rectangle(extracted_boxes, (x1, y1), (x2, y2), random_color(), 4)
    #
    # cv2.imshow('extracted_boxes', extracted_boxes)
    # cv2.waitKey()

    # convert to image segments
    rows = [image[y1: y2, x1: x2] for (x1, y1, x2, y2) in rectangles]

    return rows
