import { Component, OnInit } from '@angular/core';
import { ErrorHandler} from '@angular/core'
import {  Validators} from '@angular/forms';
import { Router } from '@angular/router';
import { RouterOutlet } from '@angular/router';
import { signUp,SignInInput,SignUpInput, signIn } from '@aws-amplify/auth';
import amplifyconfiguration from '../../amplifyconfiguration.json';
import { Amplify } from 'aws-amplify';
import { AmplifyAuthenticatorModule } from '@aws-amplify/ui-angular';
import { CommonModule } from '@angular/common';



@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  

  isSignDivVisiable: boolean  = true;
  
  
  errorMessage: string | null = null;
  constructor() {
    Amplify.configure(amplifyconfiguration );
  }

  

  
  

  service = {
    async handleSignUp(input: SignUpInput) {
      let { username, password, options } = input;
      
      // custom username and email
      username = username.toLowerCase();
      const customEmail = options?.userAttributes?.email?.toLowerCase();
      return signUp({
        username,
        password,
        options: {
          ...options,
          userAttributes: {
            ...options?.userAttributes,
            email: customEmail,
          },
        },
      });
    },
  };
  

}


