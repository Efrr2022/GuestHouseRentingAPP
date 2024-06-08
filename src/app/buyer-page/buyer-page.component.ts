import { Component } from '@angular/core';
import { CognitoServiceService } from '../services/cognito.service.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-buyer-page',
  standalone: true,
  imports: [],
  templateUrl: './buyer-page.component.html',
  styleUrl: './buyer-page.component.css'
})
export class BuyerPageComponent {
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
