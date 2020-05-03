# MV Bank Receipt OCR
An OCR server for reading bank maldivian bank receipts.
A live production build is running on [mvbankreceipt.xyz](https://mvbankreceipt.xyz) and 
a demo web app is running [here](https://mvbankreceipt.netlify.app).


## Table of Contents
- [Introduction](#folder-structure)
  - [Endpoints](#endpoints)
- [Setting up for Development](#setting-up-for-development)
  - [Testing https Connection](#testing-https-connection)
- [Deployment](#deployment)

## Introduction
The project uses [Tesseract OCR](https://github.com/tesseract-ocr/) to convert bank
receipt images into JSON. Receipts such as the one below

![Example Receipt](https://github.com/thoaif/mv-bank-receipt-ocr/raw/master/example-receipt.png)

is expected to have an out put of

```json
{
  "Amount": "2000",
  "Currency": "MVR",
  "Date": "20/01/20 00:00",
  "From": "Myself",
  "Message": "Still Waiting for Something to Happen",
  "Ref #": "1234356789ABCDEF",
  "Remarks": "This payment was never made",
  "Status": "Awaiting",
  "To": {
    "Account": "12345678910",
    "Name": "Someone you Know"
  }
}
```

### Endpoints
The only endpoint is `POST /ocr`, and requires a file field, with an image
file in .png, .jpg or .jpeg extension


## Folder Structure

```
my-app/
  README.md
  requirements.txt
  vevn/
  src/
    ocr/
        preprocess/
        text_processing/
        ocr.py
    responses.py
    temp_clearer.py
    utils.py
  cert/
```

## Setting up for Development

1. Clone the project
2. Create a virtual environment (option): `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Run locally: `python server.py`

### Testing https Connection
you can create self-signed SSL certificates to test the https connections using:

`mkdir cert`

`openssl req -x509 -newkey rsa:4096 -keyout cert/key.pem -out cert/cert.pem -days 365`

server.py will check for ssl certificates in the folder

## Deployment
Currently, the script only runs in production mode if there is are SSL certificates available. This is reinforced to
make sure sensitive information transmitted to the server is encrypted. It should also be noted that Flask is not 
the best package for creating a production-ready server.

To deploy, set `FLASK_ENV` environment variable to `production`:

`export FLASK_ENV=production`

then run python as a background process:

`nohup python3 server.py > output.log &`
