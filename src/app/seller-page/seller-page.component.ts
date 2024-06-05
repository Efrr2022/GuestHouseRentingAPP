import { Component } from '@angular/core';
import { CognitoServiceService } from '../services/cognito.service.service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-seller-page',
  standalone: true,
  imports: [],
  templateUrl: './seller-page.component.html',
  styleUrl: './seller-page.component.css'
})
export class SellerPageComponent {
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
