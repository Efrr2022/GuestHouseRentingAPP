import { Injectable } from '@angular/core';
import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserPool,
  CognitoUserSession
} from "amazon-cognito-identity-js";
import AWS from 'aws-sdk';
import * as AmazonCognitoIdentity from 'amazon-cognito-identity-js'
import { environment } from "../../environments/environment";
import { Router } from '@angular/router';

AWS.config.update({
  accessKeyId: 'AKIA2UC3FWKS4YFBXBNR', 
  secretAccessKey: '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', 
  region: environment.cognito.region 
});

@Injectable({
  providedIn: 'root'
})
export class CognitoServiceService {

  //userPool: any;
  private cognitoUser:any;
  username: string = "";
  private poolData = {
    UserPoolId: environment.cognito.userPoolId,
    ClientId: environment.cognito.userPoolWebClientId,
  };
  public userPool = new AmazonCognitoIdentity.CognitoUserPool(this.poolData)
  
  constructor(private router: Router) {
    
  }

  // Login
  login(emailaddress: any, password: any) {
    
    let authenticationDetails = new AuthenticationDetails({
      Username: emailaddress,
      Password: password,
    });
    

    this.username = emailaddress;
    //this.userPool = new CognitoUserPool(poolData);
    let userData = { Username: emailaddress, Pool: this.userPool };
    
    const cognitoUser = new CognitoUser(userData);

    
    return new Promise((resolove, reject) => {
    cognitoUser?.authenticateUser(authenticationDetails, {
      onSuccess: (session) => {
        resolove(session);
        console.log("Success Session : ", session);
      },
      onFailure: ((error: any) => {
        console.log("error", error);  
      }),
    })
    
    })
  }
    

  // First time login attempt - New password require
  changePassword(
    oldPassword: string,
    newPassword: string,
    confirmPassword: string
  ) {
    if (newPassword === confirmPassword) {
      this.cognitoUser.completeNewPasswordChallenge(
        newPassword,
        {},
        {
          onSuccess: () => {
            console.log("Reset Success");
            this.router.navigate(["/login"]);
          },
          onFailure: () => {
            console.log("Reset Fail");
          },
        }
      );
    } else {
      console.log("Password didn't Match");
    }
  }

  // Logout 
  logOut() {
    let poolData = {
      UserPoolId: environment.cognito.userPoolId,
      ClientId: environment.cognito.userPoolWebClientId,
    };
    this.userPool = new CognitoUserPool(poolData);
    this.cognitoUser = this.userPool.getCurrentUser();
    if (this.cognitoUser) {
      this.cognitoUser.signOut();
      this.router.navigate(["login"]);
    }
  }

  // sign up 
  // Register a new user with Cognito 
register(email:any, password: any, address: any, age: any,Name: any,teleNumber: any) {
  console.log("inside of the service register")
 
  this.userPool = new AmazonCognitoIdentity.CognitoUserPool(this.poolData);
 // Create attribute list
 const attributeList = [
  new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'custom:address', Value: String(address) }),
  new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'custom:age', Value: String(age )}),
  new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'custom:Name', Value: String(Name )}),
  new AmazonCognitoIdentity.CognitoUserAttribute({ Name: 'custom:teleNumber', Value: String(teleNumber )}),
  
];
console.log(attributeList);

  
 return new Promise(( resolve, reject) => {
   this.userPool.signUp (
    email,
    password,
    attributeList,
    [],
    (err: any, result: any) => {
    if (err) {
      console.log(err);
     reject(err);
     } else {
       console.log(result.user);
       console.log("waiting to add to the groups")
       // Add user to group
        const userPoolId = environment.cognito.userPoolId;
        const username = result.user.getUsername();

        // Initialize the CognitoIdentityServiceProvider
        const cognitoIdentityServiceProvider = new AWS.CognitoIdentityServiceProvider({
          region: environment.cognito.region
        });
        console.log("cognito Identity",cognitoIdentityServiceProvider )

        // Add user to group
        const groupParams = {
          GroupName: 'Seller', // replace with your group name
          UserPoolId: userPoolId,
          Username: username
        };

        console.log("groupParam", groupParams)
        cognitoIdentityServiceProvider.adminAddUserToGroup(groupParams, (err, data) => {
          if (err) {
            console.log("Error From adding to group",err);
            reject(err);
          } else {
            console.log('User added to group:', data);
          }
        });
        resolve(result.user);
     }
     }
     );
     });
   }

   // confirm the registration
	confirmRegistration(username: string, code: string) {
    console.log("I am inside of confirmation serice function")
    const userData = {
     Username: username,
     Pool: this.userPool,
     };
     console.log("The confirmation code recived is", code);
     
     const cognitoUser = new AmazonCognitoIdentity.CognitoUser(
      userData);
     
     return new Promise(( resolve, reject) => {
      
     cognitoUser.confirmRegistration(code, true, (err: any, result:any)=>{
     if (err) {
      reject (err);
      } else {
       console.log(result);
       resolve(result);
     }
     });
     })
    }

    isAuthenticated(): boolean {
      let poolData = {
        UserPoolId: environment.cognito.userPoolId,
        ClientId: environment.cognito.userPoolWebClientId,
      };
      this.userPool = new CognitoUserPool(poolData);
      this.cognitoUser = this.userPool.getCurrentUser();
      
      return this.cognitoUser != null;
    }


    getUserGroups(): Promise<string[]> {
      let poolData = {
        UserPoolId: environment.cognito.userPoolId,
        ClientId: environment.cognito.userPoolWebClientId,
      };
      this.userPool = new CognitoUserPool(poolData);
      this.cognitoUser = this.userPool.getCurrentUser();
      return new Promise((resolve, reject) => {
        this.cognitoUser?.getSession((err: any, session: CognitoUserSession) => {
          if (err) {
            reject(err);
            return;
          }
  
          const groups = session.getIdToken().payload['cognito:groups'] || [];
          resolve(groups);
        });
      });
    }
}







