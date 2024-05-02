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
    # Connect to the database
    db = connect_to_database()
    if not db:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to connect to the database'})
        }
    
    # Extract HTTP method from the request
    http_method = event["httpMethod"]
    
    if http_method == "PATCH":
        return handle_update_renter(event, db)
    elif http_method == "DELETE":
        return handle_delete_renter(event, db)
    elif http_method == "GET":
        return handle_list_renters(event, db)
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'message': 'Method Not Allowed'})
        }


def handle_update_renter(event, db):
    try:
        # Parse request body to get updated renter information
        data = json.loads(event["body"])

         # Extract renter ID from the request body
        renter_id = data.get("renterId")
        
        # Construct SQL query to update renter information
        sql_query = f"""
                    UPDATE tblRenter 
                    SET first_name = '{data.get('firstName')}',
                        last_name = '{data.get('lastName')}',
                        address = '{data.get('address')}',
                        contact_number = '{data.get('contactNumber')}',
                        email_address = '{data.get('emailAddress')}',
                        password = '{data.get('password')}',
                        last_modified = CURRENT_TIMESTAMP,
                        status = {data.get('status')}
                    WHERE renterId = {renter_id}
                    """
        
        # Create a cursor
        cursor = db.cursor()
        
        # Execute the SQL query
        cursor.execute(sql_query)
        db.commit()
        
        # Close the cursor
        cursor.close()
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Renter updated successfully'})
        }
    except Exception as e:
        # Return error response if any exception occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        # Close database connection
        db.close()



def handle_delete_renter(event, db):
    try:
        # Extract renter ID from the path parameters of the request
        renter_id = event["queryStringParameters"]["renterId"]
        
        # Construct SQL query to delete renter
        sql_query = f"""
                    DELETE FROM tblRenter
                    WHERE renterId = {renter_id}
                    """
        
        # Create a cursor
        cursor = db.cursor()
        
        # Execute the SQL query
        cursor.execute(sql_query)
        db.commit()
        
        # Close the cursor
        cursor.close()
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Renter deleted successfully'})
        }
    except Exception as e:
        # Return error response if any exception occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        # Close database connection
        db.close()

def handle_list_renters(event, db):
    try:
        # Construct SQL query to select all renters
        sql_query = """
                    SELECT renterId, first_name, last_name, address, contact_number, 
                    email_address, password, registration_time, last_modified,status
                    FROM tblRenter
                    """
        
        # Create a cursor
        cursor = db.cursor()
        
        # Execute the SQL query
        cursor.execute(sql_query)
        renters = cursor.fetchall()
        
        # Prepare response data
        response_data=[]
        for renter in renters:
            response_data.append({
                "renterId": renter[0],
                "firstName": renter[1],
                "lastName": renter[2],
                "address": renter[3],
                "contactNumber": renter[4],
                "emailAddress": renter[5],
                "registrationTime": str(renter[6]),  #.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                "lastModified": str(renter[7]),      #.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
                "status": renter[8]
        })
        
        # Close the cursor
        cursor.close()
        
        # Return success response with list of renters
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
    except Exception as e:
        # Return error response if any exception occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        # Close database connection
        db.close()































def handle_list_renters_by_house_id(event, db):
    try:
        # Extract houseId from the path parameters of the request
        house_id = event["queryStringParameters"]["houseId"]
        
        # Construct SQL query to select renters based on houseId
        sql_query = f"""
                    SELECT r.renterId, r.firstName, r.lastName, r.address, r.contactNumber, r.emailAddress, r.registrationTime, r.lastModified, r.status
                    FROM tblRenter r
                    JOIN tblHouseReserved hr ON r.renterId = hr.renterId
                    WHERE hr.houseId = {house_id}
                    """
        
        # Create a cursor
        cursor = db.cursor()
        
        # Execute the SQL query
        cursor.execute(sql_query)
        renters = cursor.fetchall()
        
        # Prepare response data
        response_data = []
        for renter in renters:
            response_data.append({
                "renterId": renter[0],
                "firstName": renter[1],
                "lastName": renter[2],
                "address": renter[3],
                "contactNumber": renter[4],
                "emailAddress": renter[5],
                "registrationTime": str(renter[6]),
                "lastModified": str(renter[7]),
                "status": renter[8]
            })
        
        # Close the cursor
        cursor.close()
        
        # Return success response with list of renters
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
    except Exception as e:
        # Return error response if any exception occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        # Close database connection
        db.close()

