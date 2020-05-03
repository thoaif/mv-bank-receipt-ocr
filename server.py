from threading import Thread

import settings as S
from flask_cors import CORS
import os
from flask import Flask, request, jsonify

from src.ocr import run_ocr
from src.temp_clearer import clear_temp
from src.utils import get_extension, is_extension_allowed, get_random_file_name, clear_file

from src.responses import no_file, no_selected_file, wrong_extension, failed_ocr

app = Flask(__name__)

app.secret_key = S.SECRET_KEY
app.config['UPLOAD_FOLDER'] = S.UPLOAD_DIR
app.config['MAX_CONTENT_LENGTH'] = S.MAX_FILE_SIZE

CORS(app)

clear_thread = Thread(target=clear_temp, daemon=True)
clear_thread.start()


@app.route('/ocr', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        if 'file' not in request.files:
            return no_file, 400

        file = request.files['file']

        if file.filename == '':
            return no_selected_file, 400

        extension = get_extension(file.filename)

        if is_extension_allowed(extension):
            # rename and save file
            file_path = get_random_file_name(extension)
            file.save(file_path)

            # predict
            resp = run_ocr(file_path)

            # if no fields - prediction failed
            if len(resp) == 0:
                return failed_ocr, 400

            # clear uploaded image
            clear_file(file_path)
            return jsonify(resp)
        else:
            return wrong_extension, 400


if __name__ == "__main__":

    certs_found = os.path.isfile('cert/cert.pem') and os.path.isfile('cert/key.pem')
    if certs_found:
        print('Found Certificates')

    if not S.IS_PRODUCTION or not certs_found:
        print('Running in Development Mode')

        args = {
            "host": "0.0.0.0",
            "port": 5000
        }

        if certs_found:
            args["ssl_context"] = ('cert/cert.pem', 'cert/key.pem')

        print('args', args)

        app.run(**args)
    else:
        from gevent.pywsgi import WSGIServer

        print('Running in Production Mode')

        server = WSGIServer(('0.0.0.0', 443), app, keyfile='cert/key.pem', certfile='cert/cert.pem')
        server.serve_forever()
