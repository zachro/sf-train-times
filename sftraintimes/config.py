import json
import logging
from os import environ

import boto3

KEY_STORAGE_BUCKET = 'sftraintimes-api-key-storage-' + environ.get('STAGE')
KEY_STORAGE_PATH = 'five_eleven_keys.json'


def get_logger():
    logger = logging.getLogger('log')
    logger.setLevel(logging.WARNING)

    return logger


def get_five_eleven_api_key():
    keys = boto3.client('s3').get_object(Bucket=KEY_STORAGE_BUCKET, Key=KEY_STORAGE_PATH)['Body'].read().decode('utf-8')
    return json.loads(keys)['api_key']
