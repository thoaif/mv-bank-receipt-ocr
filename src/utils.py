import os
import uuid
from typing import Union

import settings as S


def get_extension(filename: str) -> Union[str, None]:
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()


def is_extension_allowed(extension: Union[str, None]) -> bool:
    return extension in S.ALLOWED_EXTENSIONS


def get_random_file_name(extension: str) -> str:
    file_name = '{}.{}'.format(uuid.uuid4(), extension)
    file_path = os.path.join(S.UPLOAD_DIR, file_name)
    return file_path


def clear_file(file_path: str):
    os.remove(file_path)
