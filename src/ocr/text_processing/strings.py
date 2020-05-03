from typing import Iterable, Union


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