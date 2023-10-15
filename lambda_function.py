import json
import logging
import sys
import boto3
from boto3.session import Session
from botocore.exceptions import ClientError
import urllib3


# Initialize the log configuration using the base class
FORMAT = "ISKDataLakeETLJob %(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)s() ] %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format=FORMAT, force=True,
                    datefmt='%m-%d-%Y %I:%M:%S %p')
logger = logging.getLogger()
pinpoint = boto3.client('pinpoint')

def lambda_handler(event, context):
    
    logger.info('Lambda is running on schedule')
    project_id = '0714efdec3774d6eb50e81789f86a704'
    
    destination_number = {
        "Sam": "+1412....."
    }
  
    app_id = "0714efdec3774d6eb50e81789f86a704"
    origination_number = "+12565405619"
    caller_id = ""
    language_code = "en-US"
    voice_id = "Matthew"
    
    for name,destination in destination_number.items():
        quotes = get_quotes()
        compliments = get_compliment()
        ssml_message = (
        "<speak>"
        f"Hello Good morning! {name} wake up !!! <emphasis> Wake up! Wake up! </emphasis> "
        f"<break strength='weak'/> {compliments} "
        f"<amazon:effect phonation='soft'>Here is a quote for you! {quotes} Take care! Have a beautiful day"
        "</amazon:effect>"
        "</speak>")
        logger.info(f"Sending voice message from {origination_number} to {destination}.")
    
        message_id = send_voice_message(
            boto3.client('pinpoint-sms-voice'), origination_number, caller_id,
            destination, language_code, voice_id, ssml_message)
        logger.info(f"Message sent! to {destination} Message ID: {message_id}")
    
    
def send_voice_message(
        sms_voice_client, origination_number, caller_id, destination_number,
        language_code, voice_id, ssml_message):

    try:
        response = sms_voice_client.send_voice_message(
            DestinationPhoneNumber=destination_number,
            OriginationPhoneNumber=origination_number,
            CallerId=caller_id,
            Content={
                'SSMLMessage': {
                    'LanguageCode': language_code,
                    'VoiceId': voice_id,
                    'Text': ssml_message}})
    except ClientError:
        logger.exception(
            "Couldn't send message from %s to %s.", origination_number, destination_number)
        raise
    else:
        return response['MessageId']
        

def get_quotes():
    url = 'https://api.quotable.io/quotes/random'
    try:
        http = urllib3.PoolManager()
        r = http.request('GET', url)
        quote = r.data
        quote_str = quote.decode('utf-8')
        quote_dict = json.loads(quote_str)
        morning_quote = quote_dict[0].get("content", None)

        return morning_quote
    except Exception as e:
        logger.error(e)

def get_compliment():
    try:
        compliment_url = 'https://8768zwfurd.execute-api.us-east-1.amazonaws.com/v1/compliments'
        http = urllib3.PoolManager()
        r = http.request('GET', compliment_url)
        quote = r.data
        quote_str = quote.decode('utf-8')
        compliments = json.loads(quote_str)
        
        return compliments
    except Exception as e:
        logger.error(e)