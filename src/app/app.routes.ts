import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { AdminPageComponent } from './admin-page/admin-page.component';
import { BuyerPageComponent } from './buyer-page/buyer-page.component';
import { SellerPageComponent } from './seller-page/seller-page.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import { authGuard } from './guards/auth.guard.guard';

export const routes: Routes = [
    
  { path: 'login', component: LoginComponent },
  { path: 'admin', component: AdminPageComponent, canActivate: [authGuard] },
  { path: 'buyer', component: BuyerPageComponent, canActivate: [authGuard] },
  { path: 'seller', component: SellerPageComponent, canActivate: [authGuard] },
  { path: 'unauthorized', component: UnauthorizedComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
];