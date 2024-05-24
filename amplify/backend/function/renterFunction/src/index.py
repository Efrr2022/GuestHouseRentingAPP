import datetime
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
    query_params = event.get("queryStringParameters", {})
    
    if http_method == "GET" and query_params is not None and "houseId" in query_params:
        return handle_list_renters_by_house_id(event, db)
    elif http_method == "GET":
        return handle_list_renters(event, db)
    elif http_method == "PATCH":
        return handle_update_renter(event, db)
    elif http_method == "DELETE":
        return handle_delete_renter(event, db)
    elif http_method == "POST":
        renter_out = query_params.get("renterOut", "0")
        if renter_out == "1":
            return create_renter_out_record(event, db)
        else:
            return create_renter_in_record(event, db)
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
                    UPDATE tblRenter Set status = 0
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
                    FROM tblRenter WHERE status=1
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
                "registrationTime": renter[6],
                "lastModified": renter[7].strftime('%Y-%m-%d %H:%M:%S') if isinstance(renter[7], datetime.datetime) else renter[7], 
                "status": renter[8]
            })
            print(f"data:{renter[6]} type:{type(renter[6])}") #{renter[6].strftime('%Y-%m-%d %H:%M:%S')} isinstance: {isinstance(renter[6], datetime.datetime)}")
        
        # Close the cursor
        cursor.close()
        
        # Return success response with list of renters
        return {
            'statusCode': 200,
            'body': json.dumps(response_data, default=str)  # Serialize datetime objects using default=str
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
        house_id = event["queryStringParameters"]["houseId"]
        
        # Construct SQL query to select renters based on houseId
        sql_query = f"""
                    SELECT r.renterId, r.first_name, r.last_name, r.address, r.contact_number, r.email_address, r.registration_time, r.last_modified, r.status
                    FROM tblRenter r
                    JOIN tblLeasedHouses hr ON r.renterId = hr.renterId
                    WHERE hr.houseId = {house_id} AND r.status=1
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



def create_renter_in_record(event, db):
    try:
        # Parse request body to get renter in information
        data = json.loads(event["body"])
        
        # Extract relevant data from the request body
        leased_id = data.get("leasedId")
        stat_electricity = data.get("statElectricity")
        stat_paint = data.get("statPaint")
        no_bulbs = data.get("noBulbs")
        stat_bulbs = data.get("statBulbs")
        stat_windows = data.get("statWindows")
        status_toilet_sink = data.get("statusToiletSink")
        stat_washing_sink = data.get("statWashingSink")
        
        # Construct SQL query to insert renter in record
        sql_query = f"""
                    INSERT INTO tblRenterIn (leasedId, stat_electricity, stat_paint, no_bulbs, stat_bulbs, stat_windows, 
                    status_toiletSink, stat_washingSink, last_modified, renterInStatus)
                    VALUES ({leased_id}, '{stat_electricity}', '{stat_paint}', {no_bulbs}, '{stat_bulbs}', '{stat_windows}', 
                    '{status_toilet_sink}', '{stat_washing_sink}', CURRENT_TIMESTAMP, 1)
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
            'body': json.dumps({'message': 'Renter In record created successfully'})
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



def create_renter_out_record(event,db):

    try:
        data=json.loads(event["body"])

        leased_id=data.get("leasedId")
        stat_electricity = data.get("statElectricity")
        stat_paint = data.get("statPaint")
        no_bulbs = data.get("noBulbs")
        stat_bulbs = data.get("statBulbs")
        stat_windows = data.get("statWindows")
        status_toilet_sink = data.get("statusToiletSink")
        stat_washing_sink = data.get("statWashingSink")

        sql_query = f"""
                    INSERT INTO tblRenterOut (leasedId, stat_electricity, stat_paint, no_bulbs, stat_bulbs, stat_windows, 
                    status_toiletSink, stat_washingSink, last_modified, renterOutStatus)
                    VALUES ({leased_id}, '{stat_electricity}', '{stat_paint}', {no_bulbs}, '{stat_bulbs}', '{stat_windows}', 
                    '{status_toilet_sink}', '{stat_washing_sink}', CURRENT_TIMESTAMP, 1)
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
            'body': json.dumps({'message': 'Renter In record created successfully'})
        }   


    except Exception as e:
        # Return error response if any exception occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        db.close()