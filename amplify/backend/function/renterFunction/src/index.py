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
            # Extract renter ID from the path parameters of the request
            renter_id = event["pathParameters"]["renterId"]
            
            # Parse request body to get updated renter information
            request_body = json.loads(event["body"])
            
            # Construct SQL query to update renter information
            sql_query = f"""
                        UPDATE tblRenter 
                        SET firstName = '{request_body.get('firstName')}',
                            lastName = '{request_body.get('lastName')}',
                            address = '{request_body.get('address')}',
                            contactNumber = '{request_body.get('contactNumber')}',
                            emailAddress = '{request_body.get('emailAddress')}',
                            password = '{request_body.get('password')}',
                            lastModified = CURRENT_TIMESTAMP,
                            status = {request_body.get('status')}
                        WHERE renterId = {renter_id}
                        """
            
            # Execute the SQL query
            with db.cursor() as cursor:
                cursor.execute(sql_query)
                db.commit()
            
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
            renter_id = event["pathParameters"]["renterId"]
            
            # Construct SQL query to delete renter
            sql_query = f"""
                        DELETE FROM tblRenter
                        WHERE renterId = {renter_id}
                        """
            
            # Execute the SQL query
            with db.cursor() as cursor:
                cursor.execute(sql_query)
                db.commit()
            
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
                        SELECT renterId, firstName, lastName, address, contactNumber, emailAddress, registrationTime, lastModified, status
                        FROM tblRenter
                        """
            
            # Execute the SQL query
            with db.cursor() as cursor:
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
            house_id = event["pathParameters"]["houseId"]
            
            # Construct SQL query to select renters based on houseId
            sql_query = f"""
                        SELECT r.renterId, r.firstName, r.lastName, r.address, r.contactNumber, r.emailAddress, r.registrationTime, r.lastModified, r.status
                        FROM tblRenter r
                        JOIN tblHouseReserved hr ON r.renterId = hr.renterId
                        WHERE hr.houseId = {house_id}
                        """
            
            # Execute the SQL query
            with db.cursor() as cursor:
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
