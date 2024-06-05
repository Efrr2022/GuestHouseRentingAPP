import { CanActivateFn,Router } from '@angular/router';
import { CognitoServiceService } from '../services/cognito.service.service';
import { inject } from '@angular/core';


export const authGuard: CanActivateFn = async (route, state) => {
  const authService = inject(CognitoServiceService);
  const router = inject(Router);

  try {
    const groups = await authService.getUserGroups();
  if (!groups.length) {
    // User doesn't belong to any group, redirect to unauthorized
    return false;
  }
  
  switch (true) {
      case groups.includes('Admin'):
        console.log("I am inside guard for admin");
        router.parseUrl('/admin');
        return true;//
      case groups.includes('Buyer'):
        router.parseUrl('/buyer');
        return true;
      case groups.includes('Seller'):
        router.parseUrl('/seller');
        return true;
      default:
        return router.parseUrl('/unauthorized');
    }
  }  catch (error) {
    console.error('Error in auth guard:', error);
    return router.parseUrl('/login');
  }
};
