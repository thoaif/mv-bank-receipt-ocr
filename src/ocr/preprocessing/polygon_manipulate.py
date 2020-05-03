from typing import Union

import cv2
import numpy as np


def is_line(w: int, h: int, max_height, multiplier=0.01) -> bool:
    """
    checks whether the dimensions match that of a line
    """
    return w > h * multiplier and h < max_height


def is_approx_rect(contour: np.ndarray, confidence: int = 0.95) -> bool:
    """
    returns true if contour is approximately a rectangle for the given confidence
    """
    _, _, w, h = cv2.boundingRect(contour)
    area = w * h
    contour_area = cv2.contourArea(contour)
    return area >= confidence * contour_area


def get_approx_polygon(contour: np.ndarray, points: int = 4) -> Union[np.ndarray, None]:
    """
    gets the approximate polygon from a contour
    """
    num_points = contour.shape[0]

    # contour has less # points than target
    if num_points < points:
        return None

    processed_contour = contour
    arc_length = cv2.arcLength(processed_contour, closed=True)
    epsilon = 0.2 * arc_length
    while num_points > points:
        processed_contour = cv2.approxPolyDP(processed_contour, epsilon=epsilon, closed=True)
        num_points = processed_contour.shape[0]
        epsilon *= 1.1

    return processed_contour
