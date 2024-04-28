import json
import mysql.connector


try:
  db=mysql.connector.connect(
    host="tectown-backend-q1-2024.c1s0muoa0qc4.us-east-1.rds.amazonaws.com",
    user="admin",
    database="rentalHouses",
    password="Tectown1!"
  )
  print("database connected")
except Exception as e:
  print(f'There was an exception: {e}')


def handler(event, context):
    print('received event:')
    print(event)

    if event["httpMethod"] == "GET":
        response=handle_get_request(event)
    elif event["httpMethod"] == "POST":
        response=handle_post_request(event)
    elif event["httpMethod"] == "DELETE":
        response= handle_delete_request(event)
    elif event["httpMethod"] == "PATCH":
        response= handle_patch_request(event)
    else:
         response = {
            'statusCode': 405,
            'body': json.dumps({
                'message': 'Method Not Allowed'
            })
        }
  


    return {
        'statusCode': response.get('statusCode', 200),
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(response.get('body', {})) 
    }


# defining handle request method 
def handle_post_request(event):
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
        sql_query = f"""INSERT INTO tblHouses (houseId, house_heading, number_of_bedroom, number_of_bedroom, number_of_balcony, 
                        date_of_posting, is_active, house_description, house_number, house_floor_number, house_payment_type, house_payment_type, 
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



def handle_get_request(event):
    print('received event inside handle_get_request:')
    print(event)
    
    # db=db_connected()
    # Create a cursor object to execute SQL queries
    mycursor=db.cursor()
    query_param=event.get("queryStringParameters",None)
    if query_param is not None:
        limit = int(query_param.get('limit', 10))  # Convert limit to an integer
        offset = int(query_param.get('offset', 0))  # Convert offset to an integer
    else:
        limit=10
        offset=0
      

    sql_query=f""" SELECT *
        FROM tblHouses
        LIMIT {limit}
        OFFSET {offset};
        """
    
     # Execute a SQL query to select all records from the "Expense" table
    mycursor.execute(sql_query)
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
    
    response={}
    response["body"]=response_list
    response["statusCode"]=200
    return response

    

def handle_delete_request(event):
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
            sql_query = f"DELETE FROM tblHouses WHERE houseId = {house_id}"
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



def handle_patch_request(event):
    mycursor = db.cursor()

    try:
        # Parse request body
        data = json.loads(event['body'])

        # Extract data fields
        house_id = data.get('houseId')
        fields_to_update = data.get('fieldsToUpdate', {})  # Assuming fields to update are provided in the request body

        # Construct SQL query
        set_pairs = []
        for key, value in fields_to_update.items():
            set_pairs.append(f"{key} = '{value}'")
        set_clause = ", ".join(set_pairs)
        sql_query = f"""UPDATE tblHouses
                        SET {set_clause}
                        WHERE houseId = {house_id}"""
        
        # Execute query
        mycursor.execute(sql_query)
        db.commit()
    
        response_patch = {
            'statusCode': 200,
            'body': json.dumps('Property updated successfully')
        }
    except Exception as e:
        print(f'There was an exception: {e}')
        response_patch = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    finally:
        mycursor.close()
    
    return response_patch







