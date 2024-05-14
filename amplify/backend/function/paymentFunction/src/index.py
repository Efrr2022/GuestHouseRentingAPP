
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
        
        httpMethod=event['httpMethod']

        if httpMethod == "GET":
            if 'id' in event['queryStringParameters']:
                response = handle_get_payment(event, db)
            elif 'renterId' in event['queryStringParameters']:
                response = handle_get_payment_by_renter(event, db)
                
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({'message': 'Method Not Allowed'})
            }
        
        return {
        'statusCode': response.get('statusCode', 200),
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response.get('body'))
    }




    

def handle_get_payment(event,db):
        

        try:
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
                    'paymentDate' : str(payments[3])
                })
            print(f" type of paymentdate: {type(payments[3])}  data:{payments[3]} ")


            mycursor.close()

            response_get={
                'statusCode': 200,
                'body': json.dumps(response_list, default=str)  # Serialize datetime objects using default=str

            }

            return response_get
                   
                
        except Exception as e:
            return {
                'statusCode' : 500,
                'body' : json.dumps({'error': str(e)})
            }
        finally:
            db.close()



def handle_get_payment_by_renter(event, db):
    try:
        query_params = event.get('queryStringParameters')
        renter_id = query_params['renterId']

        mycursor = db.cursor()

        sql_query = f"""SELECT * FROM tblPayment WHERE renterId = {renter_id}"""

        mycursor.execute(sql_query)

        result = mycursor.fetchall()

        response_list = []
        for payment in result:
            response_list.append({
                'paymentId': payment[0],
                'leasedId': payment[1],
                'paymentAmount': payment[2],
                'paymentDate': str(payment[3])
            })
        print(f"Type of payment date: {type(payment[3])} Data: {payment[3]}")

        mycursor.close()

        response_get = {
            'statusCode': 200,
            'body': json.dumps(response_list, default=str)  # Serialize datetime objects using default=str
        }

        return response_get
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        db.close()
        
