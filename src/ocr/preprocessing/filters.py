import cv2
import numpy as np


def contrast_brightness(image):
    """
    gives a contrast boost to the image
    """
    contrast = 25
    brightness = -50

    image = np.int16(image)
    image += brightness

    image = image * (contrast / 127 + 1) - contrast
    image = np.clip(image, 0, 255)

    return image


def min_max_threshold(image: np.ndarray, threshold_type: int, alpha: float = 0.5) -> np.ndarray:
    """
    apply thresholding using midpoint of pixel values of images
    """
    image_max = np.max(image)
    image_min = np.min(image)
    threshold = round(image_max * alpha + image_min * (1 - alpha))
    thresholded = cv2.threshold(image, threshold, 255, threshold_type)[1]
    return thresholded
