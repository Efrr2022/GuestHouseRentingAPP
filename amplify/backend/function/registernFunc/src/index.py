import json
import sys
import mysql.connector
import logging
import boto3
from botocore.exceptions import ClientError



# Create a custom logger 
logger = logging.getLogger("register function")
        
# Create handlers
c_handler = logging.StreamHandler(stream=sys.stdout)
c_handler.setLevel(logging.INFO)
fmt = logging.Formatter(
    "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s"
)
c_handler.setFormatter(fmt)
# Add handlers to the logger
logger.addHandler(c_handler)
logger.setLevel(logging.INFO)

def get_secret():
    secret_name = "dev/rentalHouseApp"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)



def connect_to_database():
    # Fetch secrets from AWS Secrets Manager
    secrets = get_secret()

    try:
        db = mysql.connector.connect(
            host=secrets['host'],
            user=secrets['user'],
            database=secrets['database'],
            password=secrets['password']
        )
        logger.info("database connected from logger")
        print("Database connected")
        return db
    except Exception as e:
        print(f'There was an exception: {e}')


def handler(event, context):
    print('received event:')
    print(event)
  
    # Initialize Cognito client
    client = boto3.client('cognito-idp')

    # Extract user details from the event body
    body = json.loads(event.get('body', '{}'))
    postdata = body.get('postdata', {})  # Access the 'postdata' key
    username = postdata.get('username')
    password = postdata.get('password')
    email = postdata.get('email')

    if not username or not password or not email:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({'message': 'Invalid input. Username, password, and email are required.'})
        }

    try:
        # Register the user in Cognito User Pool        
        response = client.sign_up(
            ClientId='67gj73oagdf5nj1bq9n4g46d2', 
            Username=email,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
            ]
        )
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({
                'message': 'User registered successfully!',
                'response': response
            })
        }
    except ClientError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps({
                'message': 'User registration failed.',
                'error': str(e)
            })
        }
