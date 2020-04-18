import os
import time
import traceback
from pathlib import Path

import settings as S

keep_running = True


def has_expired(file_path: str) -> bool:
    created_time = os.path.getctime(file_path)
    current_time = time.time()
    return current_time - created_time > S.TTL


def clear_temp():
    while keep_running:
        print('Clearing')
        files = Path(S.UPLOAD_DIR).glob('*')
        cleared = 0
        for file in files:
            file_path = str(file)
            if has_expired(file_path):
                try:
                    os.remove(file_path)
                    cleared += 1
                except Exception as e:
                    print(e)
                    traceback.print_exc()

        if cleared > 0:
            print('Cleared {}'.format(cleared))
        time.sleep(S.CLEARING_PERIOD)
    print('Exiting Thread')

