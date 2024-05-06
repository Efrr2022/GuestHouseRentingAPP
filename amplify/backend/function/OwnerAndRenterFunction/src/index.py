import json
import mysql.connector 
import config
from botocore.exceptions import ClientError
import re
import logger
import boto3


def handler(event, context):

    # resources comes from API Gateway
    status_check_path = '/status'
    reservation_path = '/reservation'
    leased_path = '/leased'
    rate_path = '/rate'
    category_path= '/category'
    

    

    response = None
    # try and catch block to filter the path and method coming   
    try:
        # Variables to hold http method and the resource path
        http_method = event.get('httpMethod')
        path = event.get('path')
        logger.logger.info('Lambda Handler OwnerAndRenterFunction is called from API method %s and path %s ', path , http_method)
  
        # If statement for filtering the path and http method 
  
        # Check the service working or not 
        if http_method == 'GET' and path == status_check_path:
            response = build_response(200, 'Service is Operational')
############################################# GET Methods ################################################################
        # GET Method with reservation path    
        elif http_method == 'GET' and path == reservation_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,reservation_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'],reservation_path)
        # GET Method with reservation path    
        elif http_method == 'GET' and path == leased_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,leased_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'], leased_path) 
        # GET Method with rate path    
        elif http_method == 'GET' and path == rate_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,rate_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'],rate_path)
        # GET Method with reservation path    
        elif http_method == 'GET' and path == category_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,category_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'], category_path) 
####################################### End of GET Method ######################################################    

####################################### Post Methods ###########################################################
        # Post Methid for saving Reservation
        elif http_method == 'POST' and path == reservation_path:
            body =json.loads(event['body'])
            logger.logger.info("Data to save to the database", body)
            response = save_method(body,reservation_path)
        # Post Methid for saving leased Houses
        elif http_method == 'POST' and path == leased_path:
            body =json.loads(event['body'])
            logger.logger.info("Data to save to the database", body)
            response = save_method(body,leased_path)
        # Post Methid for saving rate of a house
        elif http_method == 'POST' and path == rate_path:
            body =json.loads(event['body'])
            logger.logger.info("Data to save to the database", body)
            response = save_method(body,rate_path)
        # Post Methid for saving category for rate
        elif http_method == 'POST' and path == category_path:
            body =json.loads(event['body'])
            logger.logger.info("Data to save to the database", body)
            response = save_method(body,category_path)
#################################### End of Post Methods ############################################################

#################################### PATCH Methods ##################################################################
        # Patch Method for updating reservation 
        elif http_method == 'PATCH' and path == reservation_path:
            body = json.loads(event['body'])
            response = modify_method(body['userId'],body['updateKey'],body['updateValue'],reservation_path)
        # Patch Method for updating leased houses data
        elif http_method == 'PATCH' and path == leased_path:
            body = json.loads(event['body'])
            response = modify_method(body['userId'],body['updateKey'],body['updateValue'],leased_path)
        # Patch Method for updating rate of a house
        elif http_method == 'PATCH' and path == rate_path:
            body = json.loads(event['body'])
            response = modify_method(body['userId'],body['updateKey'],body['updateValue'],rate_path)
        # Patch Method for updating category for category houses data
        elif http_method == 'PATCH' and path == category_path:
            body = json.loads(event['body'])
            response = modify_method(body['userId'],body['updateKey'],body['updateValue'],category_path)
################################### End of Patch methods #############################################################

################################### Delete Methods ####################################################################
        # Delete Method for deleting a reservation of a house record
        elif http_method == 'DELETE' and path == reservation_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,reservation_path)
        # Delete Method for deleting a leased record
        elif http_method == 'DELETE' and path ==leased_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,leased_path)
        # Delete Method for deleting a rate of a house record
        elif http_method == 'DELETE' and path == rate_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,rate_path)
        # Delete Method for deleting a category record
        elif http_method == 'DELETE' and path ==category_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,category_path)
##################################  End of Delete Methods ###############################################################

    # If exception happens 
    except Exception as e:
        logger.logger.error("Exception Occured",exc_info=True )
        response = build_response(400, f"Error Processing Request {e}")
    # Return Value to api  
    return response

    #Close Session. 


###################################### Function to get  with Limit and Offset ##############################  
def get_method(limit,offset,userPath):
    
    logger.logger.info("i am inisde block get user")
    db = connect_to_database()
    mycursor = db.cursor()
    logger.logger.info("My Currsor connected to the database")
    # Block for reterving data from owner table
    if userPath == '/owner':
        logger.logger.info("inside if block of owner path")
        stmt = f"SELECT * From tblOwner LIMIT {limit} OFFSET {offset};"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        logger.logger.info(result)
        if result:
           table_data = []
           for row in result:
               logger.logger.info(row[6])
               table_data.append({
               'userId': row[0],
               'firstName': row[1],
               'userPassword': row[2],
               'lastName': row[3],
               'address': row[4],
               'Contact Number': row[5],
               'Date of birth': row[6],
               'lastName': row[7],
               'address': row[8]
               })
        logger.logger.info("data to return", table_data)
               
    #Block fo selecting data from renter table  
    else:
        logger.logger.info("inside if block of renter path")
        stmt = f"SELECT * From tblRenter LIMIT {limit} OFFSET {offset}"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        if result:
            table_data = []
            for row in result:
                table_data.append({
               'userId': row[0],
               'first Name': row[1],
               'last Name': row[2],
               'address': row[3],
               'Contact Number': row[4],
               'Email Address': row[5],
               'Password': row[6],
               'Registration Time': row[7].strftime("%d-%m-%Y"),
               'last_modified': row[8].strftime("%d-%m-%Y"),
               'Status': row[9]
            }) 
            logger.logger.info("data to return", table_data)
                
    mycursor.close()
    db.close()
    return build_response(200, table_data)
############################### End of Functon Users #############################################################

############################## Function for for saving to the database ######################################

def save_method(request_body,userPath):
  # Block for saving Owner records
  logger.logger.info("Inside block code of save user")
  db = connect_to_database()
  mycursor = db.cursor()
  logger.logger.info("My Currsor connected to the database", mycursor)
  
  if userPath == '/owner':
      logger.logger.info("I am inside block owner safe")
      try:
          # To check Wether table users is available or not
          stmt = "SHOW TABLES LIKE 'tblOwner'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()
          x = request_body


          # To prepare to the value to insert to the database 
          val = []
          if result:
              email = request_body["email_address"]
              if is_valid_email(email):
              
                val.append((x["first_name"], x["userPassword"], x["last_name"], x["address"], x["contact_number"], \
                                x["date_of_birth"], x["gender"], x["email_address"],x["occupation"], x["registration_time"], \
                                x["last_modified"], x["userStatus"],x["profile_image"]),)
                # Sql statement to insert data to the database  
                sql="Insert into tblOwner (first_name,userPassword,last_name,address,contact_number,date_of_birth,gender, \
                email_address,occupation,registration_time,last_modified,userStatus,profile_image) values (%s, %s, %s, %s,%s, %s, \
                %s, %s,%s, %s, %s, %s,%s)"
                mycursor.executemany(sql,val)
                db.commit()  
                body = {
                     'Operation': 'SAVE',
                     'Message': 'SUCCESS',
                     'Item': request_body
                      }
                StatusCode = 201
                logger.logger.info("Body to return %s and Status Code %s", body,StatusCode) 
              else:
                body = "Invalid Email Address"
                StatusCode = 400  
                logger.logger.error(body)  
          # If table Users not found 
          else:
              body = "Table Owner doesn't found"
              StatusCode = 400
              logger.logger.error(body)
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
  # Block for saving rental records
  else: 
      try:
          # To check Wether table users is available or not
          stmt = "SHOW TABLES LIKE 'tblRenter'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()
          x = request_body
          # To prepare to the value to insert to the database 
          val = []
          if result:
              if is_valid_email(x["email_address"]):
                  val.append((x["first_name"], x["last_name"], x["address"], x["contact_number"], \
                            x["email_address"], x["password"], x["registration_time"], \
                            x["last_modified"], x["status"]),)
                  # Sql statement to insert data to the database  
                  sql="Insert into tblRenter (first_name,last_name,address,contact_number,email_address,password, \
                  registration_time,last_modified,status) values (%s, %s, %s, %s,%s, %s, \
                  %s, %s,%s)"
                  mycursor.executemany(sql,val)
                  db.commit()  
                  body = {
                     'Operation': 'SAVE',
                     'Message': 'SUCCESS',
                     'Item': request_body
                      }
                  StatusCode = 201
                  logger.logger.info("Body to return %s and Status Code %s", body,StatusCode) 
              else:
                body = "Invalid Email Address"
                StatusCode = 400
                logger.logger.error(body)
              
          # If table Users not found 
          else:
              body = "Table Renter doesn't found"
              StatusCode = 400
              logger.logger.error(body)
          mycursor.close()
          db.close()
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
     
############################## End of function save_user(body)###########################################

############################## Function For updater  #################################################
def modify_method(userId, updateKey, updateValue,userPath):
  # Block of code for updating owner record
  db = connect_to_database()
  mycursor = db.cursor()
  logger.logger.info("My Currsor connected to the database", mycursor)
  
  if userPath == '/owner':
    sql = f"select * from tblOwner where ownerId={userId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        if updateKey == "email_address" :
         if is_valid_email(updateValue):
            sql = f"UPDATE tblOwner SET {updateKey}=\"{updateValue}\" WHERE ownerId={userId};"
            mycursor.execute(sql)
            db.commit()
            sql = f"select * from tblOwner where ownerId={userId}"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            table_data = {
                    'ownerId': row[0],
                    'firstName': row[1],
                    'userPassword': row[2],
                    'lastName': row[3],
                    'address': row[4],
                    'Contact Number': row[5],
                    'Date of birth': row[6].strftime("%d-%m-%Y"),
                    'gender': row[7],
                    'email address': row[8]
                }
            
            body = {
                'Operation': 'Update',
                'Message': 'SUCCESS',
                'Owner User': table_data
        
             }
            status_code = 200
            logger.logger.info("return data: %s with statuscode %s", body,status_code)
         else: 
           body = "Invalid Email Address"
           status_code = 400
           logger.logger.error(body)
        else: 
            sql = f"UPDATE tblOwner SET {updateKey}=\"{updateValue}\" WHERE ownerId={userId};"
            mycursor.execute(sql)
            db.commit()
            sql = f"select * from tblOwner where ownerId={userId}"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            table_data = {
                    'ownerId': row[0],
                    'firstName': row[1],
                    'userPassword': row[2],
                    'lastName': row[3],
                    'address': row[4],
                    'Contact Number': row[5],
                    'Date of birth': row[6].strftime("%d-%m-%Y"),
                    'gender': row[7],
                    'email address': row[8]
                }
                 
            body = {
                'Operation': 'Update',
                'Message': 'SUCCESS',
                'Owner User': table_data
        
             }
            status_code = 200
            logger.logger.info("return data: %s with statuscode %s", body,status_code)
            
        
    else:
        
        body = {
            'Message': f'Owner With Id={userId} not found'
        }
        print(body)
        status_code = 204
        logger.logger.error(body)

  # Block of code for updating record of renter      
  elif userPath == '/renter':
    logger.logger.info("inside modify renter")
    sql = f"select * from tblRenter where renterID={userId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    logger.logger.info("Data before updated",result)
    if result:
       if updateKey == "email_address" :
         if is_valid_email(updateValue):
            sql = f"UPDATE tblRenter SET {updateKey}=\"{updateValue}\" WHERE renterId={userId};"
            mycursor.execute(sql)
            db.commit()
            sql = f"select * from tblRenter where renterId={userId}"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            table_data = {
                    'renterId': row[0],
                    'first Name': row[1],
                    'last Name': row[2],
                    'address': row[3],
                    'Contact Number': row[4],
                    'Email Address': row[5],
                    'Password': row[6],
                    'Registration Time': row[7].strftime("%d-%m-%Y"),
                    'last_modified': row[8].strftime("%d-%m-%Y"),
                    'Status': row[9]
              }
            
            body = {
                'Operation': 'Update',
                'Message': 'SUCCESS',
                'renter User': table_data
            
            }
            status_code = 200
            logger.logger.info("return data: %s with statuscode %s", body,status_code)
         else: 
           body = "Invalid Email Address"
           status_code = 400
           logger.logger.error(body)
       else: 
          sql = f"UPDATE tblRenter SET {updateKey}=\"{updateValue}\" WHERE renterId={userId};"
          mycursor.execute(sql)
          db.commit()
          sql = f"select * from tblRenter where renterId={userId}"
          mycursor.execute(sql)
          row = mycursor.fetchone()
          table_data = {
                    'renterId': row[0],
                    'first Name': row[1],
                    'last Name': row[2],
                    'address': row[3],
                    'Contact Number': row[4],
                    'Email Address': row[5],
                    'Password': row[6],
                    'Registration Time': row[7].strftime("%d-%m-%Y"),
                    'last_modified': row[8].strftime("%d-%m-%Y"),
                    'Status': row[9]
              }
          print(table_data)
          body = {
                'Operation': 'Update',
                'Message': 'SUCCESS',
                'renter User': table_data
            
            }
          status_code = 200
          logger.logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
           'Message': f'renter With Id={userId} not found'
        }
        print(body)
        status_code = 204
        logger.logger.error(body)
  mycursor.close()
  db.close()
  return build_response(status_code, body)
########################################### End of Function update##############################################


############################## Function to delete ##################################################
def delete_method(id,userPath):
  db = connect_to_database()
  mycursor = db.cursor()
  logger.logger.info("My Currsor connected to the database", mycursor)
  if userPath == '/owner':
    sql = f"select * from tblOwner where ownerId={id}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        sql = f"Delete from tblOwner WHERE ownerId={id}"
        mycursor.execute(sql)
        db.commit()
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            }
        status_code = 200
        logger.logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
            'Message': f'Owner with Id = {id} not found'
        }
        status_code = 204
        logger.logger.error(body)
  elif userPath == '/renter':
    sql = f"select * from tblRenter where renterId={id}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        sql = f"Delete from tblRenter WHERE renterId={id}"
        mycursor.execute(sql)
        db.commit()
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            }
        status_code = 200
        logger.logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
            'Message': f'Owner with Id = {id} not found'
        }
        status_code = 204
        logger.logger.error(body)
  mycursor.close()
  db.close()
  return build_response(status_code, body)
############################## End of delete Function ################################################



############################## Function for building responses to API #######################################


def build_response(status_code, body):
    return {
     "statusCode": status_code,
	 "body": json.dumps(body),
	 "headers": {
	     "Content-Type": "application/json"
		   }
   	}
   	
################################ End of Build response ####################################################

############################### Function to check wether an email is valid or not #########################

def is_valid_email(email):

    """Check if the email is a valid format."""

    # Regular expression for validating an Email

    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'

    # If the string matches the regex, it is a valid email

    if re.match(regex, email):

        return True

    else:

        return False

########################### End of function is_valid_email #############################

########################## Function to Connect to the database ########################
def connect_to_database():
   secrets = get_secret()
   host_url = secrets['host']
   user_name = secrets['user']
   database_dev = secrets['database']
   password_database = secrets['password']
   
   '''' host_url = config.secret.host '''''
   ''''user_name = config.secret.user '''''
   '''''password_database= config.secret.password'''''
   '''''database_dev = config.secret.database'''''

   # Credentials for connecting to the database 
   try:
        mydb = mysql.connector.connect(
            host = host_url,
            user = user_name,
            password = password_database,
            database = database_dev

            )
        logger.logger.info("Connected to the database Successfully")
   except Exception as e:
       logger.logger.error("Can not connect to the database error occured", exc_info=True)
   return mydb
####################### End of Function connect_to_database ####################################


####################### Secret manager Configuration ###########################################
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
   

 
 
   

  
  