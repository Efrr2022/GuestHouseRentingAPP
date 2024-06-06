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
        logger.info("database connected from logger")
        print("Database connected")
        return db
    except Exception as e:
        print(f'There was an exception: {e}')

def handler(event, context):
    print("inside property function")
    logger.info("logger message")
    print('Received event:')
    print(event)

    # Connect to the database
    db = connect_to_database()

    if not db:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to connect to the database'})
        }


    if event["httpMethod"] == "GET":
        response = handle_get_request(event, db)
    elif event["httpMethod"] == "POST":
        response = handle_post_request(event, db)
    elif event["httpMethod"] == "DELETE":
        response = handle_delete_request(event, db)
    elif event["httpMethod"] == "PATCH":
        response = handle_update_house_with_features(event, db)
    else:
        response = {
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

  


# defining handle request method 
def handle_post_request(event,db):
    
    mycursor = db.cursor()

    try:
        # Parse request body
        data = json.loads(event['body'])

        # Extract data fields
        house_id = data.get('houseId')
        house_heading = data.get('houseHeading')
        number_of_bedroom = data.get('numberOfBedroom')
        number_of_bathroom = data.get('numberOfBathroom')
        number_of_balcony = data.get('numberOfBalcony')
        date_of_posting = data.get('dateOfPosting')
        is_active = data.get('isActive')
        house_description = data.get('houseDescription')
        house_number = data.get('houseNumber')
        house_floor_number = data.get('houseFloorNumber')
        house_payment_type = data.get('housePaymentType')
        location_id = data.get('locationId')
        is_verified = data.get('isVerified')
        price = data.get('price')
        owner_id = data.get('ownerId')
        last_modified = data.get('lastModified')
        area = data.get('area')
        house_type = data.get('houseType')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        house_status = data.get('houseStatus')  

        # Construct SQL query
        sql_query = f"""INSERT INTO tblHouses (houseId, house_heading, number_of_bedroom,number_of_bathroom, number_of_balcony, 
                        date_of_posting, is_active, house_description, house_number, house_floor_number, house_payment_type, location_id,
                        is_verified, price, ownerId, last_modified, area, house_type, latitude, longitude, houseStatus) 
                        VALUES ({house_id}, '{house_heading}', {number_of_bedroom}, {number_of_bathroom}, {number_of_balcony}, 
                        '{date_of_posting}', {is_active}, '{house_description}', '{house_number}', {house_floor_number}, 
                        '{house_payment_type}', {location_id}, {is_verified}, {price}, {owner_id}, '{last_modified}', 
                        {area}, {house_type}, {latitude}, {longitude}, {house_status})"""
        

        
        # Execute query
        mycursor.execute(sql_query)
        db.commit()
        
    
        response_post={
            'statusCode': 200,
            'body': json.dumps('Property added successfully')
        }
    except Exception as e:  
        print(f'There was an exception: {e}')
        response_post = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    finally:
        mycursor.close()
    return response_post



def handle_get_request(event, db):
    # logging.info("Received event inside handle_get_request:")
    # logging.info(event)
    

    try:
        print("Received event inside handle_get_request:")
    
        # Create a cursor object to execute SQL queries
        mycursor = db.cursor()
        
        query_params = event.get("queryStringParameters", None)
        if query_params is not None:
            limit = int(query_params.get('limit', 10))  
            offset = int(query_params.get('offset', 0)) 
            no_of_bedrooms = int(query_params.get('noOfBedrooms',None)) 
            no_of_bathrooms = int(query_params.get('noOfBathrooms',None))  
            price = int(query_params.get('price',None))
        else:
            limit = 10
            offset = 0
            no_of_bedrooms = None
            no_of_bathrooms = None
            price=None

        # Construct the base SQL query
        sql_query = """
            SELECT *
            FROM tblHouses
            WHERE houseStatus=1
        """

        # Add WHERE clause for filtering based on parameters
        conditions = []
        if no_of_bedrooms is not None:
            conditions.append(f"number_of_bedroom = {no_of_bedrooms}")
        if no_of_bathrooms is not None:
            conditions.append(f"number_of_bathroom = {no_of_bathrooms}")
        if price is not None:
            conditions.append(f"price >= {price}")
    
        
        if conditions:
            sql_query += " AND " + " AND ".join(conditions)

        # Add LIMIT and OFFSET for pagination
        sql_query += f" LIMIT {limit} OFFSET {offset};"
        mycursor.execute(sql_query)
        # logging.info('executed query')
        print("executed query")

        # Fetch all the rows from the result set
        result = mycursor.fetchall()

        # Prepare response data
        response_list = []
        for row in result:
            response_list.append({
                "houseId": row[0],  
                "houseHeading": row[1],  
                "numberOfBedroom": row[2],  
                "numberOfBathroom": row[3],  
                "numberOfBalcony": row[4],  
                "dateOfPosting": str(row[5]),  
                "isActive": row[6],  
                "houseDescription": row[7],  
                "houseNumber": row[8],  
                "houseFloorNumber": row[9],  
                "housePaymentType": row[10],  
                "locationId": row[11],  
                "isVerified": row[12],  
                "price": float(row[13]), 
                "ownerId": row[14],  
                "lastModified": str(row[15]), 
                "area": row[16], 
                "houseType": row[17],  
                "latitude": float(row[18]),  
                "longitude": float(row[19]),  
                "houseStatus": row[20]  
            })

        # Close the cursor, but do not close the database connection
        mycursor.close()

        # Construct response object 
        response = {
            "statusCode": 200,
            "body": response_list
        }
        return response

    except Exception as e:
        # logging.error(f'Error executing SQL query: {e}')
        # Return error response
        print(f"Error in try block: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    finally:
        db.close()



def handle_delete_request(event,db):
    mycursor = db.cursor()

    try:
        # Extract house IDs to delete from query parameters
        query_params = event.get("queryStringParameters", {})
        house_ids_str = query_params.get('houseIds', '')
        # house_ids = [int(id) for id in house_ids_str.split(',') if id.strip()]
        house_ids = []
        for id_str in house_ids_str.split(','):
            if id_str.strip():
                house_ids.append(int(id_str))

        if not house_ids:
            raise ValueError("No house IDs provided for deletion.")

        # Construct SQL query for each house ID
        for house_id in house_ids:
            sql_query = f" UPDATE tblHouses Set houseStatus = 0 WHERE houseId = {house_id}"
            mycursor.execute(sql_query)
        
        db.commit()

        response_delete = {
            'statusCode': 200,
            'body': json.dumps('Houses deleted successfully')
        }
    except Exception as e:
        print(f'There was an exception: {e}')
        response_delete = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    finally:
        mycursor.close()
    
    return response_delete



def handle_update_house_with_features(event, db):
    try:
        # Parse request body
        data = json.loads(event['body'])

        # Extract data for updating the house
        house_data = {
            "houseId": data.get("houseId"),
            "houseHeading": data.get("houseHeading"),
        }

        # Extract data for updating house features (amenities)
        features_data = {
            "houseId": data.get("houseId"),
            "numberOfCarParking": data.get("numberOfCarParking"),
            "hasCarpet": data.get("hasCarpet"),
        }

        # Construct SQL query to update house
        house_sql_query = f"""
                            UPDATE tblHouses
                            SET house_heading = '{house_data['houseHeading']}'
                            WHERE houseId = {house_data['houseId']}
                            """
        
        # Construct SQL query to update house features
        features_sql_query = f"""
                                UPDATE tblHouseFeatures
                                SET num_of_car_parking = {features_data['numberOfCarParking']},
                                    has_carpet = {features_data['hasCarpet']}
                                WHERE houseId = {features_data['houseId']}
                                """

        # Open a cursor
        cursor = db.cursor()

        # Execute the SQL queries
        cursor.execute(house_sql_query)
        cursor.execute(features_sql_query)
        db.commit()

        # Close the cursor
        cursor.close()

        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'House and amenities updated successfully'})
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









