import { Component, Input,OnInit, Inject } from '@angular/core';
import { Router,ActivatedRoute } from '@angular/router';
import { CognitoServiceService } from '../../services/cognito.service.service';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';


@Component({
  selector: 'app-otp-verify',
  standalone: true,
  imports: [ReactiveFormsModule,CommonModule],
  templateUrl: './otp-verify.component.html',
  styleUrl: './otp-verify.component.scss'
})
export class OtpVerifyComponent {
  @Input() email: any = '';
  errorMessage: string = '';
  
  constructor (
    public dialogRef: MatDialogRef<OtpVerifyComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private authService: CognitoServiceService,
     private router:Router,
     private route: ActivatedRoute
     ) {}
  protected codeForm = new FormGroup({
    code: new FormControl('', [Validators.required,]),
    
  })
 
  verifyOtp() {
    const username = this.email;
    console.log(" I am inside the otp verification function")
    console.log('username', username);
  
    if (username){
     if (this.codeForm.value.code) {
      this.authService
      .confirmRegistration(username, this.codeForm.value.code)
         .then((result) => {
          // OTP verification successful
        console.log('OTP verification successful', result);
        this.dialogRef.close(true);
        this.refreshPage();

        })
        .catch((error) => {
        this.errorMessage = 'OTP Verification Failed. Check Your OTP code.'
        console.error('OTP verfication failed',error);
     });
        } else {
        this.errorMessage = 'User is not autehnticated. Please log '
        
        }
        
      }}

      closeDialog() {
        this.dialogRef.close(false); // Close dialog without success indication
      }

      refreshPage() {
        window.location.reload();
      }
}
