import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { CognitoServiceService } from '../../services/cognito.service.service';
import { OtpVerifyComponent } from '../otp-verify/otp-verify.component';
import { MatDialog } from '@angular/material/dialog'; 
import { CommonModule } from '@angular/common';
import { inject } from '@angular/core'; 


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ ReactiveFormsModule, RouterModule,CommonModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  

  errorMessage: string='';
  isSignDivVisiable: boolean  = true;

  userPool: any;
  cognitoUser: any;
  username: string = "";
  constructor(
    private authService: CognitoServiceService,
    private router: Router,
    private dialog: MatDialog) {}
  
  protected loginForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required])
  })

  protected registerForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required]),
    phoneNumber: new FormControl('', [Validators.required])
  })


  register() {
    
    console.log("inside the function of register of login componenet")
    this.authService
    .register(this.registerForm.value.email, this.registerForm.value.password,
              this.registerForm.value.phoneNumber)
    .then((user) => {
   
    const dialogRef = this.dialog.open(OtpVerifyComponent, {
     width: '300px', 
    
     });
     dialogRef.componentInstance.email = this.registerForm.value.email;
     
     
     })
     .catch((error) => {
     console.error('Registration error:', error);
     });
     }


  login () {
    if(this.loginForm.valid) {
    this.authService
    .login(this.loginForm.value.email, this.loginForm.value.password)
    .then((result:any) => {
    console.log(result.idToken.payload);
    const user = {
    username: result.idToken.payload.email,
    // Add any other user attributes you want to store
    };
    console.log(user);
    //Authentication successful, you can navigate to the home page or perform other actions.
    console.log('Authentication Succcessful', result);
    this.router.navigate(['/home'], {state: {user} });
    })
    .catch((error) => {
    this.errorMessage = 'Authentication failed. Please check your credentials.';
    console.error('Authentication failed', error);
    });
    }else {
    this.errorMessage = 'Please provide a username and Password.';
    }
}
}



