import json
import logging
import sys
import mysql.connector
import boto3
from botocore.exceptions import ClientError

# Create a custom logger 
logger = logging.getLogger("Property function")
        
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
        logger.info("Database connected")
        return db
    except Exception as e:
        logger.error(f'There was an exception: {e}')

def login_handler(event, context):
    print("Received event:")
    print(event)

    # Initialize Cognito client
    client = boto3.client("cognito-idp")

    # Extract user credentials from the event body
    body = json.loads(event.get("body", "{}"))
    username = body.get("username")
    password = body.get("password")

    if not username or not password:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({"message": "Invalid input. Username and password are required."}),
        }

    try:
        # Authenticating the user
        response = client.initiate_auth(
            ClientId="67gj73oagdf5nj1bq9n4g46d2",  
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
            },
        )

        # Return the authentication tokens (ID, Access, and Refresh tokens)
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "message": "Login successful.",
                "id_token": response["AuthenticationResult"]["IdToken"],
                "access_token": response["AuthenticationResult"]["AccessToken"],
                "refresh_token": response["AuthenticationResult"]["RefreshToken"],
            }),
        }
    except ClientError as e:
        error_message = e.response["Error"]["Message"]
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": json.dumps({
                "message": "Login failed.",
                "error": error_message,
            }),
        }
