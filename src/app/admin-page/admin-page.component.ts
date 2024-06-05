import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CognitoServiceService } from '../services/cognito.service.service';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [],
  templateUrl: './admin-page.component.html',
  styleUrl: './admin-page.component.css'
})
export class AdminPageComponent {
  constructor(private cognitoService: CognitoServiceService, private router: Router) {}

  async signOut() {
    try {
      await this.cognitoService.logOut();
      this.router.navigate(['/login']); // Redirect to login after signout
    } catch (error) {
      console.error('Signout error:', error);
      // Handle signout error (optional)
    }
  }
}
