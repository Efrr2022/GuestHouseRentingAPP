import json
import mysql.connector

import boto3
from botocore.exceptions import ClientError


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


    # Your code goes here.
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
        print("Database connected")
        return db
    except Exception as e:
        print(f'There was an exception: {e}')

def handler(event, context):
    print('received event:')
    print(event)

    db = connect_to_database()

    if not db:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to connect to the database'})
        }
    
    httpMethod=event['httpMehtod']

    if httpMethod == "GET":
        response=handle_get_payment(event,db)

  
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps('Hello from your new Amplify Python lambda!')
    }




def handle_get_payment(event,db):
    pass
