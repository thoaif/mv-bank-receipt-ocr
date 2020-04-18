import os
import uuid

HOME = os.environ['HOME']

# app settings
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))
IS_PRODUCTION = os.environ.get('FLASK_ENV', 'development') != 'development'

# upload directory clearing thread settings
TTL = 10 * 60
CLEARING_PERIOD = TTL // 2

# upload options
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024
UPLOAD_DIR = os.environ.get('UPLOAD_DIR', os.path.join(HOME, 'ocr-tmp-uploads'))

os.makedirs(UPLOAD_DIR, exist_ok=True)