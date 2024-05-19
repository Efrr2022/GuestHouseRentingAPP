import json
import mysql.connector 
from botocore.exceptions import ClientError
import re
import boto3
import logging
from datetime import datetime, timedelta
import sys
from decimal import Decimal


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
    leased_path = '/leased'
    reservation_path = '/reservation'
    rate_path = '/rate'
    category_path = '/category'
    

    

    response = None
    # try and catch block to filter the path and method coming   
    try:
        # Variables to hold http method and the resource path
        http_method = event.get('httpMethod')
        path = event.get('path')
        logger.info('Lambda Handler Reservation and Leased House Function is called from API method %s and path %s ', path , http_method)
  
        # If statement for filtering the path and http method 
  
        # Check the service working or not 
        if http_method == 'GET' and path == status_check_path:
            response = build_response(200, 'Service is Operational')
###################################### Get Method ################################################################
        # GET Method with leased path    
        elif http_method == 'GET' and path == leased_path:
            if event['queryStringParameters'] == None:
             response = get_method(10,1,leased_path)
            else:
             response = get_method(event['queryStringParameters']['page_size'],event['queryStringParameters']['page_number'],leased_path)
        # GET Method with reservation path    
        elif http_method == 'GET' and path == reservation_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,reservation_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'], reservation_path)  
        # GET Method with rate path    
        elif http_method == 'GET' and path == rate_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,rate_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'],rate_path)
        # GET Method with category path    
        elif http_method == 'GET' and path == category_path:
            if event['queryStringParameters'] == None:
             response = get_method(5,0,category_path)
            else:
             response = get_method(event['queryStringParameters']['limit'],event['queryStringParameters']['offset'], category_path)      
##################################### End of Get Method ############################################################# 


##################################### Post Method ############################################################# 

        # Post Method for saving leased houses
        elif http_method == 'POST' and path == leased_path:
            body =json.loads(event['body'])
            logger.info("Data to save to the database", body)
            response = save_method(body,leased_path)
        # Post Methid for saving reservation of a house
        elif http_method == 'POST' and path == reservation_path:
            body =json.loads(event['body'])
            logger.info("Data to save to the database", body)
            response = save_method(body,reservation_path)
        # Post Method for saving rate of a houses
        elif http_method == 'POST' and path == rate_path:
            body =json.loads(event['body'])
            logger.info("Data to save to the database", body)
            response = save_method(body,rate_path)
        # Post Methid for saving category
        elif http_method == 'POST' and path == category_path:
            body =json.loads(event['body'])
            logger.info("Data to save to the database", body)
            response = save_method(body,category_path)
##################################### End of Post Method ############################################################# 


#####################################  Patch Method ############################################################# 

        # Patch Method for updating leased data
        elif http_method == 'PATCH' and path == leased_path:
            body = json.loads(event['body'])
            logger.info("leased Id %s, field to update %s, value %s ",body['methodId'],body['updateKey'],body['updateValue'] )
            response = modify_method(body['methodId'],body['updateKey'],body['updateValue'],leased_path)
        # Patch Method for updating reservation data
        elif http_method == 'PATCH' and path == reservation_path:
            body = json.loads(event['body'])
            logger.info("reservation Id %s, field to update %s, value %s ",body['methodId'],body['updateKey'],body['updateValue'] )
            response = modify_method(body['methodId'],body['updateKey'],body['updateValue'],reservation_path)
         # Patch Method for updating rate data
        elif http_method == 'PATCH' and path == rate_path:
            body = json.loads(event['body'])
            logger.info("Rate Id %s, field to update %s, value %s ",body['methodId'],body['updateKey'],body['updateValue'] )
            response = modify_method(body['methodId'],body['updateKey'],body['updateValue'],rate_path)
        # Patch Method for updating renters data
        elif http_method == 'PATCH' and path == category_path:
            body = json.loads(event['body'])
            logger.info("Category Id %s, field to update %s, value %s ",body['methodId'],body['updateKey'],body['updateValue'] )
            response = modify_method(body['methodId'],body['updateKey'],body['updateValue'],category_path)
##################################### End of Patch Method ############################################################# 

##################################### Delete Method ############################################################# 

        # Delete Method for deleting a leased record
        elif http_method == 'DELETE' and path == leased_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,leased_path)
        # Delete Method for deleting a reservation record
        elif http_method == 'DELETE' and path == reservation_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,reservation_path)
         # Delete Method for deleting a rate record
        elif http_method == 'DELETE' and path == rate_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,rate_path)
        # Delete Method for deleting a category record
        elif http_method == 'DELETE' and path == category_path:
            id = event['queryStringParameters']['id']
            response = delete_method(id,category_path)

##################################### End of Delete Method ############################################################# 

    # If exception happens 
    except Exception as e:
        logger.error("Exception Occured",exc_info=True )
        response = build_response(400, f"Error Processing Request {e}")
    # Return Value to api  
    return response

    #Close Session. 


###################################### Function to get methods with Limit and Offset ##############################  
def get_method(page_size,page_number,methodPath):
    
    logger.info("i am inisde block get method")
    logger.info(page_size)
    logger.info(page_number)
    db = connect_to_database()
    mycursor = db.cursor()
    logger.info("My Currsor connected to the database")
    # Block for reterving data from leased table
    if methodPath == '/leased':
        logger.info("inside if block of leased path")
        stmt = "SELECT * From tblLeasedHouses  Where leasedStatus=1"
       
        
        mycursor.execute(f'SELECT CAST(COUNT(*) AS UNSIGNED)FROM ({stmt}) AS subquery')
        total_count, = mycursor.fetchone()
        logger.info(total_count)
        
               
    #Block fo selecting data from reservation table  
    elif methodPath == "/reservation":
        logger.info("inside if block of reservation path")
        stmt = f"SELECT * From tblHouseReserved LIMIT {limit} OFFSET {offset}"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        if result:
            table_data = []
            for row in result:
                table_data.append({
               'reservatio id': row[0],
               'rentier id': row[1],
               'houseId': row[2],
               'date in': row[3].strftime("%d-%m-%Y"),
               'date out': row[4].strftime("%d-%m-%Y"),
               'price': row[5],
               'total': row[6],
               'last modified': row[7].strftime("%d-%m-%Y"),
               'reserved status': row[8],
               
            }) 
            logger.info( table_data)
    #Block fo selecting data from  table rate  
    elif methodPath == "/rate":
        logger.info("inside if block of rate path")
        stmt = f"SELECT * From tblRate LIMIT {limit} OFFSET {offset}"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        if result:
            table_data = []
            for row in result:
                table_data.append({
               'rate id': row[0],
               'leased id': row[1],
               'rate category id': row[2],
               'rate': row[3],
               'rate description': row[4],
               'last modified': row[5].strftime("%d-%m-%Y"),
               'rate status': row[6],
               
            }) 
            logger.info( table_data)

    #Block fo selecting data from category table  
    elif methodPath == "/category":
        logger.info("inside if block of category path")
        stmt = f"SELECT * From tblRateCategory LIMIT {limit} OFFSET {offset}"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        if result:
            table_data = []
            for row in result:
                table_data.append({
               'rate category id': row[0],
               'category name': row[1],
               'last modified': row[2].strftime("%d-%m-%Y"),
               'status': row[3],
               
            }) 
            logger.info( table_data)
                
    mycursor.close()
    db.close()
    return build_response(200, stmt, total_count, page_size, page_number)
############################### End of Functon methods #############################################################

############################## Function for for saving method to the database ######################################

def save_method(request_body,methodPath):
  now = datetime.now()
  
  logger.info("Inside block code of save method")
  try: 
    db = connect_to_database()
    mycursor = db.cursor(buffered=True)
    logger.info("My Currsor connected to the database")
    # Block for saving leased information of a house 
    if methodPath == '/leased':
      logger.info("I am inside if block of leased house  ")
      try:
          # To check Wether table leased house is available or not
          stmt = "SHOW TABLES LIKE 'tblLeasedHouses'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()
         
          x = request_body
          houseId = x["houseId"]
          start = x["date in"]
          end = x["date out"]
          
          
          stmt1= f"SELECT * \
                   FROM tblLeasedHouses \
                   WHERE houseId = '{houseId}' \
                   AND time_to >= '{start}' \
                   AND time_from <= '{end}';" 
          
          
          
          mycursor.execute(stmt1)
          check1 = mycursor.fetchmany()
          logger.info("To Check weather there is record or not in the given timeframe")
          logger.info(check1)

         
          
          # To prepare to the value to insert to the database 
          val = []
          if result:
            if start < end :
                if check1 == []:
                   stmt2= f"SELECT * \
                   FROM tblHouseReserved \
                   WHERE houseId = '{houseId}' \
                   AND date_in ='{start}' \
                   AND date_out ='{end}';"
                   mycursor.execute(stmt2)
                   check2 = mycursor.fetchmany()
                   logger.info(stmt2)
                   logger.info("To check weather it is oready booked or not")
                   logger.info(check2)
                   if check2:
                        stmt3 = f"Delete from tblHouseReserved \
                            WHERE houseId = '{houseId}' \
                            AND date_out ='{start}' \
                            AND date_in ='{end}';"
                        mycursor.execute(stmt3)
                        db.commit()
                        logger.info("The record deleted successfully from house reserved table")
                        val.append((x["date in"], x["date out"], x["price"], x["discount"], x["total"], \
                                    x["rentier grad"], x["renter grade"], x["houseId"], now, x["rentier id"], x["leased status"]),)
                        # Sql statement to insert data to the database  
                        sql="Insert into tblLeasedHouses (time_from,time_to,price,discount,price_total,rentier_grade_description, \
                        renter_grade_description,houseId,last_modified,renterId,leasedStatus) values (%s, %s, %s, %s,%s, %s, \
                        %s, %s,%s, %s, %s)"
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
                        StatusCode = 400
                        body = "There is no any record of this selecion in the house reserved"
                else:
                    StatusCode = 400
                    body = "The house is Leased. Please change date."
            else:
               StatusCode = 400
               body = "Please check the selection of your time range. Wrong date range!!!"
              
          # If table methods not found 
          else:
              body = "Table leased houses doesn't found"
              StatusCode = 400
              logger.error(body)
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
    # Block for saving reserved houses records
    elif methodPath == "/reservation": 
      logger.info("I am inside if block of reserved house")
      try:
          # To check Wether table reserved house is available or not
          stmt = "SHOW TABLES LIKE 'tblHouseReserved'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()
          x = request_body
          # To prepare to the value to insert to the database 
          houseId = x["houseId"]
          start = x["date in"]
          end = x["date out"]
          print(houseId, start, end)
          stmt1 = f"SELECT * \
                   FROM tblHouseReserved \
                   WHERE houseId = '{houseId}' \
                   AND date_out >= '{start}' \
                   AND date_in <= '{end}';"
          
          mycursor.execute(stmt1)
          check1 = mycursor.fetchmany()
          logger.info("From statement 1")
          logger.info(check1)
          stmt2= f"SELECT * \
                   FROM tblLeasedHouses \
                   WHERE houseId = '{houseId}' \
                   AND time_to >= '{start}' \
                   AND time_from <= '{end}';" 
          
          
          
          mycursor.execute(stmt2)
          check2 = mycursor.fetchmany()
          logger.info("From statement 2")
          logger.info(check2)
          val = []
          if result:
            if start < end :
                if check1 == [] and check2 == []:
              
                  val.append((x["renterId"], x["houseId"], x["date in"], x["date out"], \
                            x["price"], x["total"],  \
                            now, x["reserved Status"]),)
                  # Sql statement to insert data to the database  
                  sql="Insert into tblHouseReserved (renterId,houseId,date_in,date_out,price,total, \
                  last_modified,reservedStatus) values (%s, %s, %s, %s,%s, %s, \
                  %s, %s)"
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
                    StatusCode = 400
                    body = "The house is reserved or Leased. Please change date."
            else:
               StatusCode = 400
               body = "Please check the selection of your time range, date out must be after date in."
          
          # If table methods not found 
          else:
              body = "Table resrved house doesn't found"
              StatusCode = 400
              logger.error(body)
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
  # Block for saving rate information of a house 
    elif methodPath == '/rate':
      logger.info("I am inside if block of rate house  ")
      try:
          # To check Wether table rate is available or not
          stmt = "SHOW TABLES LIKE 'tblRate'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()
          x = request_body
          # To prepare to the value to insert to the database 
          val = []
          if result:
                val.append(( x["lease id"], x["rate category id"], x["rate"], x["rate description"], \
                                now, x["rate status"]),)
                # Sql statement to insert data to the database  
                sql="Insert into tblRate (leasedId,rateCategoryId,rate,rateDes,last_modified,rateStatus) values ( %s, %s, %s,%s, %s, \
                %s)"
                mycursor.executemany(sql,val)
                db.commit()  
                body = {
                     'Operation': 'SAVE',
                     'Message': 'SUCCESS',
                     'Item': request_body
                      }
                StatusCode = 201
                logger.info("Body to return %s and Status Code %s", body,StatusCode) 
              
          # If table methods not found 
          else:
              body = "Table leased houses doesn't found"
              StatusCode = 400
              logger.error(body)
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
    # Block for saving category rate records
    elif methodPath == "/category": 
      logger.info("I am inside if block of category house  ")
      try:
          # To check Wether table category rate is available or not
          stmt = "SHOW TABLES LIKE 'tblRateCategory'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()
          x = request_body
          # To prepare to the value to insert to the database 
          val = []
          if result:
              
                  val.append((x["category name"],
                            now, x["category Status"]),)
                  # Sql statement to insert data to the database  
                  sql="Insert into tblRateCategory (category_name, \
                  last_modified,status) values (%s, %s, %s)"
                  mycursor.executemany(sql,val)
                  db.commit()  
                  body = {
                     'Operation': 'SAVE',
                     'Message': 'SUCCESS',
                     'Item': request_body
                      }
                  StatusCode = 201
                  logger.info("Body to return %s and Status Code %s", body,StatusCode) 
             
              
          # If table methods not found 
          else:
              body = "Table Category of rate doesn't found"
              StatusCode = 400
              logger.error(body)
  
          return build_response(StatusCode,body)
      except ClientError as e:
           logger.exception("Excpetion Occured", exc_info=True)
           return build_response(400, e.response['Error']['Message'])
  finally:
      mycursor.close()
      db.close()
     
############################## End of function save_method(body)###########################################

############################## Function For updater method #################################################
def modify_method(methodId, updateKey, updateValue,methodPath):
  # Block of code for updating owner record
  db = connect_to_database()
  mycursor = db.cursor()
  logger.info("My Currsor connected to the database", mycursor)
  
  if methodPath == '/owner':
    sql = f"select * from tblOwner where ownerId={methodId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        if updateKey == "email_address" :
         if is_valid_email(updateValue):
            sql = f"UPDATE tblOwner SET {updateKey}=\"{updateValue}\" WHERE ownerId={methodId};"
            mycursor.execute(sql)
            db.commit()
            sql = f"select * from tblOwner where ownerId={methodId}"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            table_data = {
                    'ownerId': row[0],
                    'firstName': row[1],
                    'methodPassword': row[2],
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
                'Owner method': table_data
        
             }
            status_code = 200
            logger.info("return data: %s with statuscode %s", body,status_code)
         else: 
           body = "Invalid Email Address"
           status_code = 400
           logger.error(body)
        else: 
            sql = f"UPDATE tblOwner SET {updateKey}=\"{updateValue}\" WHERE ownerId={methodId};"
            mycursor.execute(sql)
            db.commit()
            sql = f"select * from tblOwner where ownerId={methodId}"
            mycursor.execute(sql)
            row = mycursor.fetchone()
            table_data = {
                    'ownerId': row[0],
                    'firstName': row[1],
                    'methodPassword': row[2],
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
                'Owner method': table_data
        
             }
            status_code = 200
            logger.info("return data: %s with statuscode %s", body,status_code)
            
        
    else:
        
        body = {
            'Message': f'Owner With Id={methodId} not found'
        }
        print(body)
        status_code = 204
        logger.error(body)

  # Block of code for updating record of renter      
  elif methodPath == '/renter':
    logger.info("inside modify renter")
    sql = f"select * from tblRenter where renterID={methodId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    logger.info("Data before updated",result)
    if result:
       if updateKey == "email_address" :
         if is_valid_email(updateValue):
            sql = f"UPDATE tblRenter SET {updateKey}=\"{updateValue}\" WHERE renterId={methodId};"
            mycursor.execute(sql)
            db.commit()
            sql = f"select * from tblRenter where renterId={methodId}"
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
                'renter method': table_data
            
            }
            status_code = 200
            logger.info("return data: %s with statuscode %s", body,status_code)
         else: 
           body = "Invalid Email Address"
           status_code = 400
           logger.error(body)
       else: 
          sql = f"UPDATE tblRenter SET {updateKey}=\"{updateValue}\" WHERE renterId={methodId};"
          mycursor.execute(sql)
          db.commit()
          sql = f"select * from tblRenter where renterId={methodId}"
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
                'renter method': table_data
            
            }
          status_code = 200
          logger.info("return data: %s with statuscode %s", body,status_code)
    else:
        body = {
           'Message': f'renter With Id={methodId} not found'
        }
        print(body)
        status_code = 204
        logger.error(body)
  mycursor.close()
  db.close()
  return build_response(status_code, body)
########################################### End of Function update_method##############################################


############################## Function to delete a method ##################################################
def delete_method(id,methodPath):
  db = connect_to_database()
  mycursor = db.cursor()
  logger.info("My Currsor connected to the database", mycursor)
  if methodPath == '/owner':
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
  elif methodPath == '/renter':
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
############################## End of delete_method Function ################################################



############################## Function for building responses to API #######################################


def build_response(status_code, query,total_count,page_size,page_number):
    logger.info("I am inside build respose function")
    db = connect_to_database()
    if page_number < 1:
      raise ValueError("Invalid page number")
    # Calculate total pages on first request to avoid redundant queries
    total_pages = int((total_count - 1) / page_size) + 1
    if page_number > total_pages:
      raise ValueError("Page number exceeds total pages")
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    paginated_query = f"{query} LIMIT {page_size}, OFFSET {start_index}"
    mycursor = db.cursor()
    mycursor.execute(paginated_query)
    data = mycursor.fetchall()
    logger.info(data)
    mycursor.close()
    db.close()
    return {
    
     "statusCode": status_code,
	 "body": json.dumps({
       "data": [dict(row) for row in data],  # Convert rows to dictionaries
       "page": page_number,
       "page_size": page_size,
       "total_pages": total_pages, 
       
       },cls=DecimalEncoder),
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
        logger.info("Connected to the database rentalHouse Successfully")
    
   except Exception as e:
       logger.error("Can not connect to the database error occured", exc_info=True)
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

########################### Decimal Encoder for JSON data
class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)


 
 
   

  
  