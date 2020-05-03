import cv2
import numpy as np

WIDTH = 500
MAX_HEIGHT = 1200


def min_max_standardize(image: np.ndarray) -> np.ndarray:
    """
    apply min max standardization
    """
    image = image.astype(np.float)
    image_max = np.max(image)
    image_min = np.min(image)
    image = (image - image_min) / (image_max - image_min)
    image = np.rint(image * 255).astype(np.uint8)

    return image


def standardize_dimension(image: np.ndarray, width: int, max_height: int) -> np.ndarray:
    """
    scale image by width while keeping the aspect ratio and does not exceed max_height
    """
    height_, width_ = image.shape[:2]
    ratio = height_ / width_
    new_height = round(ratio * width)

    if new_height > max_height:
        new_height = max_height
        width = new_height / ratio

    return cv2.resize(image, (width, new_height))


def standardize(image: np.ndarray) -> np.ndarray:
    # standardize the width
    image = standardize_dimension(image, WIDTH, MAX_HEIGHT)

    # convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image = min_max_standardize(image)

    return image
