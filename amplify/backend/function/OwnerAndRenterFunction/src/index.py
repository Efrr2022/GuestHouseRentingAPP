import json
import mysql.connector 
import base64
import config
from botocore.exceptions import ClientError
import datetime

host_url = config.secret.host
user_name = config.secret.user
password_database= config.secret.password
database_dev = config.secret.database

# resources comes from API Gateway
status_check_path = '/status'
owner_path = '/owner'
renter_path = '/renter'

# Credentials for connecting to the database 
mydb= mysql.connector.connect(
    host = host_url,
    user = user_name,
    password = password_database,
    database = database_dev

    )


def handler(event, context): 
    response = None
    # try and catch block to filter the path and method coming   
    try:
        # Variables to hold http method and the resource path
        http_method = event.get('httpMethod')
        path = event.get('path')
        print(path)
        print(http_method)
  
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
            print(body)
            response = save_user(body,owner_path)
        # Post Methid for saving renters
        elif http_method == 'POST' and path == renter_path:
            body =json.loads(event['body'])
            response = save_user(body,renter_path)

        # Patch Method for updating owners data
        elif http_method == 'PATCH' and path == owner_path:
            body = json.loads(event['body'])
            print(body['updateKey'])
            print(body['updateValue'])
            response = modify_user(body['userId'],body['updateKey'],body['updateValue'],owner_path)
        # Patch Method for updating renters data
        elif http_method == 'PATCH' and path == renter_path:
            body = json.loads(event['body'])
            print(body['updateKey'])
            print(body['updateValue'])
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
        response = build_response(400, f"Error Processing Request {e}")
    # Return Value to api  
    return response

#Close Session. 


###################################### Function to get Users with Limit and Offset ##############################  
  
def get_users(limit,offset,userPath):
    print("i am inisde block get user")
    mycursor = mydb.cursor()
    print(f"Database connected {mycursor} Successfully")
    # Block for reterving data from owner table
    if userPath == '/owner':
        print("inside if of owner path")
        stmt = f"SELECT * From tblOwner LIMIT {limit} OFFSET {offset};"
        mycursor.execute(stmt)
        result = mycursor.fetchall()
        if result:
           table_data = []
           for row in result:
               table_data.append({
               'userId': row[0],
               'firstName': row[1],
               'userPassword': row[2],
               'lastName': row[3],
               'address': row[4],
               'Contact Number': row[5],
               'Date of birth': row[6].strftime("%d-%m-%Y"),
               'lastName': row[7],
               'address': row[8]
        })
               
    #Block fo selecting data from renter table  
    else:
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
    mycursor.close()
    mydb.close()
    return build_response(200, table_data)
############################### End of Functon Users #############################################################

############################## Function for for saving User to the database ######################################

def save_user(request_body,userPath):
  mycursor = mydb.cursor()
  print("Hiii from save_user function")
  # Block for saving Owner records
  if userPath == '/owner':
      print("i am inside block owner safe")
      try:
          # To check Wether table users is available or not
          stmt = "SHOW TABLES LIKE 'tblOwner'"
          print(stmt)
          mycursor.execute(stmt)
          result = mycursor.fetchone()
          print(result)

          # To prepare to the value to insert to the database 
          val = []
          if result:
              for x in request_body:
                  val.append((x["first_name"], x["userPassword"], x["last_name"], x["address"], x["contact_number"], \
                            x["date_of_birth"], x["gender"], x["email_address"],x["occupation"], x["registration_time"], \
                            x["last_modified"], x["userStatus"],x["profile_image"]),)
                  
              print(val)
              # Sql statement to insert data to the database  
              sql="Insert into tblOwner (first_name,userPassword,last_name,address,contact_number,date_of_birth,gender, \
              email_address,occupation,registration_time,last_modified,userStatus,profile_image) values (%s, %s, %s, %s,%s, %s, \
              %s, %s,%s, %s, %s, %s,%s)"
              mycursor.executemany(sql,val)
              mydb.commit()  
              body = {
                     'Operation': 'SAVE',
                     'Message': 'SUCCESS',
                     'Item': request_body
                      }
          # If table Users not found 
          else:
              body = "Table Owner doesn't found"
          return build_response(201,body)
      except ClientError as e:
           return build_response(400, e.response['Error']['Message'])
  # Block for saving rental records
  else: 
      try:
          # To check Wether table users is available or not
          stmt = "SHOW TABLES LIKE 'tblRenter'"
          mycursor.execute(stmt)
          result = mycursor.fetchone()

          # To prepare to the value to insert to the database 
          val = []
          if result:
              for x in request_body:
                  val.append((x["first_name"], x["last_name"], x["address"], x["contact_number"], \
                            x["email_address"], x["password"], x["registration_time"], \
                            x["last_modified"], x["status"]),)
              print(val)
              # Sql statement to insert data to the database  
              sql="Insert into tblRenter (first_name,last_name,address,contact_number,email_address,password, \
              registration_time,last_modified,status) values (%s, %s, %s, %s,%s, %s, \
              %s, %s,%s)"
              mycursor.executemany(sql,val)
              mydb.commit()  
              body = {
                     'Operation': 'SAVE',
                     'Message': 'SUCCESS',
                     'Item': request_body
                      }
          # If table Users not found 
          else:
              body = "Table Renter doesn't found"
          mycursor.close()
          mydb.close()
          return build_response(201,body)
      except ClientError as e:
           return build_response(400, e.response['Error']['Message'])
     
############################## End of function save_user(body)###########################################

############################## Function For updater User #################################################
def modify_user(userId, updateKey, updateValue,userPath):
  mycursor = mydb.cursor()
  print(updateKey)
  print(updateValue)

  # Block of code for updating owner record
  if userPath == '/owner':
    sql = f"select * from tblOwner where ownerId={userId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        sql = f"UPDATE tblOwner SET {updateKey}={updateValue} WHERE ownerId={userId};"
        mycursor.execute(sql)
        mydb.commit()
        sql = f"select * from tblOwner where ownerId={userId}"
        mycursor.execute(sql)
        value = mycursor.fetchone()
        if result:
            table_data = []
            for row in result:
                table_data.append({
               'ownerId': row[0],
               'firstName': row[1],
               'userPassword': row[2],
               'lastName': row[3],
               'address': row[4],
               'Contact Number': row[5],
               'Date of birth': row[6].strftime("%d-%m-%Y"),
               'lastName': row[7],
               'address': row[8]
        }) 
        result = json.loads(table_data)
        body = {
        'Operation': 'Update',
        'Message': 'SUCCESS',
        'User': result
        }
        status_code = 200
    else:
        body = {
        'Message': f'Owner With Id={userId} not found'
        }
        status_code = 204

  # Block of code for updating record of renter      
  elif userPath == '/renter':
    sql = f"select * from tblRenter where renterID={userId}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        sql = f"UPDATE tblRenter SET {updateKey}={updateValue} WHERE renterId={userId};"
        mycursor.execute(sql)
        mydb.commit()
        sql = f"select * from tblRenter where renterId={userId}"
        mycursor.execute(sql)
        result = mycursor.fetchone()
        if result:
            table_data = []
            for row in result:
                table_data.append({
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
        }) 
        result = json.loads(table_data)
        body = {
        'Operation': 'Update',
        'Message': 'SUCCESS',
        'User': result
        }
        status_code = 200
    else:
        body = {
        'Message': f'renter With Id={userId} not found'
        }
        status_code = 204
  mycursor.close()
  mydb.close()
  return build_response(status_code, body)
########################################### End of Function update_user##############################################


############################## Function to delete a user ##################################################
def delete_user(id,userPath):
  mycursor = mydb.cursor()
  if userPath == '/owner':
    sql = f"select * from tblOwner where ownerId={id}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        sql = f"Delete from tblOwner WHERE userId={id}"
        mycursor.execute(sql)
        mydb.commit()
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            }
        status_code = 200
    else:
        body = {
            'Message': f'Owner with Id = {id} not found'
        }
        status_code = 204
  elif userPath == '/renter':
    sql = f"select * from tblRenter where renterId={id}"
    mycursor.execute(sql)
    result = mycursor.fetchone()
    if result:
        sql = f"Delete from tblRenter WHERE renterId={id}"
        mycursor.execute(sql)
        mydb.commit()
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            }
        status_code = 200
    else:
        body = {
            'Message': f'Owner with Id = {id} not found'
        }
        status_code = 204
  mycursor.close()
  mydb.close()
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

 
 
   

  
  