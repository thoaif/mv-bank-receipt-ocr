from typing import Iterable

from src.ocr.text_processing.strings import remove_and_strip, clear_lines

FIELDS = ['Status', 'Message', 'Ref #', 'Reference #', 'Date', 'From', 'To', 'Amount', 'Remarks']


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
