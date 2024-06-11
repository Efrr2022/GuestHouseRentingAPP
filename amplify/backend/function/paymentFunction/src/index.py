
import json
import sys
import mysql.connector
import logging
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

def handler(event, context):
        logger.info('received event:')
        logger.info(f'event: {event}')

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
        elif httpMethod == "DELETE" :
             response=handle_delete_payment_request(event,db)      
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

            sql_query=f"""Select * from tblPayment where paymentId = {paymentId} AND paymentStatus=1"""

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
            logger.info(f" type of paymentdate: {type(payments[3])}  data:{payments[3]} ")


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

        sql_query = f"""SELECT * FROM tblPayment WHERE renterId = {renter_id} AND paymentStatus=1"""

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
        logger.info(f"Type of payment date: {type(payment[3])} Data: {payment[3]}")

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


def handle_delete_payment_request(event,db):
    

    try:
        mycursor = db.cursor()
        query_params=event.get('queryStringParameters')
        paymentId=query_params['id']

        if not paymentId:
            raise ValueError("No paymentId provided for deletion.")

        sql_query = f" UPDATE tblPayment Set paymentStatus = 0 WHERE paymentId = {paymentId}"
        mycursor.execute(sql_query)
        
        db.commit()

        response_delete = {
            'statusCode': 200,
            'body': json.dumps('Houses deleted successfully')
        }
    except Exception as e:
        logger.error(f'There was an exception: {e}')
        response_delete = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    finally:
        mycursor.close()
    
    return response_delete
        
