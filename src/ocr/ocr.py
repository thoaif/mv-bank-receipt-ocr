import copy
from typing import Iterable, Union

from PIL import Image
import pytesseract
import cv2
import numpy as np

from src.ocr.preprocessing.filters import contrast_brightness
from src.ocr.preprocessing.row_processing import get_rows
from src.ocr.preprocessing.standardize import standardize, min_max_standardize

FIELDS = ['Status', 'Message', 'Ref #', 'Reference #', 'Date', 'From', 'To', 'Amount', 'Remarks']

WIDTH = 500


def find_target(targets: Iterable, line: str) -> Union[None, str]:
    """
    tries to find a target from a list of targets
    """
    gen = (item for item in targets if item in line)
    return next(gen, None)


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
    image = standardize(image)

    # get row segments
    rows = get_rows(image)

    predictions = {}
    remaining_fields = copy.copy(FIELDS)

    for row in rows:
        # apply some filtering to the row
        row = contrast_brightness(row)
        row = min_max_standardize(row)

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
