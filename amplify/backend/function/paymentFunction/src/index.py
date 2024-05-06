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
    else:
        response = {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }

  
    return {
        'statusCode': response.get('statusCode'),
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response.get('body'))
    }




def handle_get_payment(event,db):
    query_params=event.get('queryStringParameters')
    paymentId=query_params['id']

    mycursor=db.cursor()

    sql_query=f"""Select * from tblPayment where paymentId = {paymentId}"""

    mycursor.execute(sql_query)

    result = mycursor.fetchall()

    response_list=[]
    for payments in result:
        response_list.append({
            'paymentId' : payments[0],
            'leasedId' : payments[1],
            'paymentAmount' : payments[2],
            'paymentDate' : payments[3]
        })

    mycursor.close()

    response={}
    response["body"]=response_list
    response["statusCode"]=200
    return response

