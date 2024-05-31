import { Injectable } from '@angular/core';
import {
  AuthenticationDetails,
  CognitoUser,
  CognitoUserPool,
  CognitoUserAttribute
} from "amazon-cognito-identity-js";
import * as AmazonCognitoIdentity from 'amazon-cognito-identity-js'
import { environment } from "../../environments/environment";
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class CognitoServiceService {

  //userPool: any;
  cognitoUser: any;
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
    cognitoUser.authenticateUser(authenticationDetails, {
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
register(email:any, password: any, phoneNumber: any) {
  console.log("inside of the service register")
 // let poolData = {
    //UserPoolId: environment.cognito.userPoolId,
   // ClientId: environment.cognito.userPoolWebClientId,
  //};
  const attributeList: AmazonCognitoIdentity.CognitoUserAttribute [] = [] ;
  // Add the name attribute
 attributeList.push;{
  new AmazonCognitoIdentity.CognitoUserAttribute ( {
   Name: 'phoneNumber',
   Value: phoneNumber,
  })
};

 /** const attributeList = [
    new CognitoUserAttribute({ Name: 'gender', Value: gender }),
    new CognitoUserAttribute({ Name: 'phoneNumber', Value: phoneNumber }), // Add the given_name attribute
    new CognitoUserAttribute({ Name: 'givenName', Value: givenName }),
    new CognitoUserAttribute({ Name: 'familyName', Value: familyName }),
    new CognitoUserAttribute({ Name: 'middleName', Value: middleName})
  ];*/
    //this.userPool = new CognitoUserPool(this.poolData);
  
 
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
       resolve (result.user);
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
}







