import json
import logging

import boto3

from sftraintimes.service import UserService, StopService, LineService
from sftraintimes.dao import UserDAO
from sftraintimes.client import FiveElevenClient
from sftraintimes.controller import SetupController

KEY_STORAGE_BUCKET = 'sftraintimes-api-key-storage'
KEY_STORAGE_PATH = 'five_eleven_keys.json'


user_service = None
stop_service = None
setup_controller = None


def get_user_service():
    if not user_service:
        return UserService(UserDAO(boto3.resource('dynamodb').Table(UserDAO.USER_TABLE_NAME)))
    return user_service


def get_stop_service():
    if not stop_service:
        return StopService(FiveElevenClient(_get_five_eleven_api_key()))
    return stop_service


def get_setup_controller():
    if not setup_controller:
        return SetupController(LineService(FiveElevenClient))
    return setup_controller


def get_logger():
    logger = logging.getLogger('log')
    logger.setLevel(logging.WARNING)

    return logger


def _get_five_eleven_api_key():
    keys = boto3.client('s3').get_object(Bucket=KEY_STORAGE_BUCKET, Key=KEY_STORAGE_PATH)['Body'].read().decode('utf-8')
    return json.loads(keys)['api_key']
