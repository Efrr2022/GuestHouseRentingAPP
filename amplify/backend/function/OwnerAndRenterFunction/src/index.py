import json
import mysql.connector 
import config
from botocore.exceptions import ClientError
import re
import logging
import sys
# Create a custom logger
logger = logging.getLogger("lambdaOwnerAndRental")
        
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
   
  
def handler(event, context):
    
    

    # resources comes from API Gateway
    status_check_path = '/status'
    owner_path = '/owner'
    renter_path = '/renter'
    

    

    response = None
    # try and catch block to filter the path and method coming   
    try:
        # Variables to hold http method and the resource path
        http_method = event.get('httpMethod')
        path = event.get('path')
        logger.info('Lambda Handler OwnerAndRenterFunction is called from API method %s and path %s ', path , http_method)
  
        # If statement for filtering the path and http method 
  
        # Check the service working or not 
        if http_method == 'GET' and path == status_check_path:
            response = build_response(200, 'Service is Operational')

        # GET Method with owner path    
        elif http_method == 'GET' and path == owner_path:
            if event['queryStringParameters'] == None:
             response = get_users(5,0,owner_path)
            else:
             response = get_users(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'],owner_path)
        # GET Method with renter path    
        elif http_method == 'GET' and path == renter_path:
            if event['queryStringParameters'] == None:
             response = get_users(5,0,renter_path)
            else:
             response = get_users(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'], renter_path)   

        # Post Methid for saving owners
        elif http_method == 'POST' and path == owner_path:
            body =json.loads(event['body'])
            logger.info("Data to save to the database", body)
            response = save_user(body,owner_path)
        # Post Methid for saving renters
        elif http_method == 'POST' and path == renter_path:
            body =json.loads(event['body'])
            logger.info("Data to save to the database", body)
            response = save_user(body,renter_path)

        # Patch Method for updating owners data
        elif http_method == 'PATCH' and path == owner_path:
            body = json.loads(event['body'])
            logger.info("Owner Id %s, field to update %s, value %s ",body['userId'],body['updateKey'],body['updateValue'] )
            response = modify_user(body['userId'],body['updateKey'],body['updateValue'],owner_path)
        # Patch Method for updating renters data
        elif http_method == 'PATCH' and path == renter_path:
            body = json.loads(event['body'])
            logger.info("Owner Id %s, field to update %s, value %s ",body['userId'],body['updateKey'],body['updateValue'] )
            response = modify_user(body['userId'],body['updateKey'],body['updateValue'],renter_path)

        # Delete Method for deleting a owner record
        elif http_method == 'DELETE' and path == owner_path:
            id = event['queryStringParameters']['id']
            response = delete_user(id,owner_path)
        # Delete Method for deleting a owner record
        elif http_method == 'DELETE' and path == renter_path:
            id = event['queryStringParameters']['id']
            response = delete_user(id,renter_path)

    # If exception happens 
    except Exception as e:
        logger.error("Exception Occured",exc_info=True )
        response = build_response(400, f"Error Processing Request {e}")
    # Return Value to api  
    return response

    #Close Session. 


###################################### Function to get Users with Limit and Offset ##############################  
def get_users(limit,offset,userPath):
    
    logger.info("i am inisde block get user")
    db = connect_to_database()
    mycursor = db.cursor()
    logger.info("My Currsor connected to the database")
    # Block for reterving data from owner table
    if userPath == '/owner':
        logger.info("inside if block of owner path")
        stmt = f"SELECT * From tblOwner LIMIT {limit} OFFSET {offset};"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        logger.info(result)
        if result:
           table_data = []
           for row in result:
               logger.info(row[6])
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
        logger.info("data to return", table_data)
               
    #Block fo selecting data from renter table  
    else:
        logger.info("inside if block of renter path")
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
        logger.info("data to return", table_data)
                
    mycursor.close()
    db.close()
    return build_response(200, table_data)
############################### End of Functon Users #############################################################

############################## Function for for saving User to the database ######################################

def save_user(request_body,userPath):
  # Block for saving Owner records
  logger.info("Inside block code of save user")
  db = connect_to_database()
  mycursor = db.cursor()
  logger.info("My Currsor connected to the database", mycursor)
  
  if userPath == '/owner':
      logger.info("I am inside block owner safe")
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
                logger.info("Body to return %s and Status Code %s", body,StatusCode) 
              else:
                body = "Invalid Email Address"
                StatusCode = 400  
                logger.error(body)  
          # If table Users not found 
          else:
              body = "Table Owner doesn't found"
              StatusCode = 400
              logger.error(body)
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.exception("Excpetion Occured", exc_info=True)
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
                  logger.info("Body to return %s and Status Code %s", body,StatusCode) 
              else:
                body = "Invalid Email Address"
                StatusCode = 400
                logger.error(body)
              
          # If table Users not found 
          else:
              body = "Table Renter doesn't found"
              StatusCode = 400
              logger.error(body)
          mycursor.close()
          db.close()
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
     
############################## End of function save_user(body)###########################################

############################## Function For updater User #################################################
def modify_user(userId, updateKey, updateValue,userPath):
  # Block of code for updating owner record
  db = connect_to_database()
  mycursor = db.cursor()
  logger.info("My Currsor connected to the database", mycursor)
  
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
            logger.info("return data: %s with statuscode %s", body,status_code)
         else: 
           body = "Invalid Email Address"
           status_code = 400
           logger.error(body)
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
            logger.info("return data: %s with statuscode %s", body,status_code)
            
        
    else:
        
        body = {
            'Message': f'Owner With Id={userId} not found'
        }
        print(body)
        status_code = 204
        logger.error(body)

  # Block of code for updating record of renter      
  elif userPath == '/renter':
    logger.info("inside modify renter")
    sql = f"select * from tblRenter where renterID={userId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    logger.info("Data before updated",result)
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
            logger.info("return data: %s with statuscode %s", body,status_code)
         else: 
           body = "Invalid Email Address"
           status_code = 400
           logger.error(body)
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
          logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
           'Message': f'renter With Id={userId} not found'
        }
        print(body)
        status_code = 204
        logger.error(body)
  mycursor.close()
  db.close()
  return build_response(status_code, body)
########################################### End of Function update_user##############################################


############################## Function to delete a user ##################################################
def delete_user(id,userPath):
  db = connect_to_database()
  mycursor = db.cursor()
  logger.info("My Currsor connected to the database", mycursor)
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
        logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
            'Message': f'Owner with Id = {id} not found'
        }
        status_code = 204
        logger.error(body)
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
        logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
            'Message': f'Owner with Id = {id} not found'
        }
        status_code = 204
        logger.error(body)
  mycursor.close()
  db.close()
  return build_response(status_code, body)
############################## End of delete_user Function ################################################



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
   host_url = config.secret.host
   user_name = config.secret.user
   password_database= config.secret.password
   database_dev = config.secret.database

   # Credentials for connecting to the database 
   try:
        mydb = mysql.connector.connect(
            host = host_url,
            user = user_name,
            password = password_database,
            database = database_dev

            )
        logger.info("Connected to the database Successfully")
   except Exception as e:
       logger.error("Can not connect to the database error occured", exc_info=True)
   return mydb
   

 
 
   

  
  