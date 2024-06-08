import { Injectable } from '@angular/core';
import { from, throwError, firstValueFrom } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { CognitoIdentityClient } from '@aws-sdk/client-cognito-identity';
import { fromCognitoIdentityPool } from '@aws-sdk/credential-provider-cognito-identity';
import {
  SecretsManagerClient,
  GetSecretValueCommand,
  GetSecretValueCommandOutput,
} from '@aws-sdk/client-secrets-manager';
import AWS from 'aws-sdk';
import { environment } from "../../environments/environment";

@Injectable({
  providedIn: 'root',
})
export class AwsSecretsManagerService {
  private identityPoolId = environment.cognito.IdentityPoolId; // Replace with your Identity Pool ID
  private region = 'us-east-1'; // Replace with your region
  private cognitoClient: CognitoIdentityClient;

  constructor() {
    this.cognitoClient = new CognitoIdentityClient({ region: this.region });
  }

  getCredentials() {
    return from(
      fromCognitoIdentityPool({
        client: this.cognitoClient,
        identityPoolId: this.identityPoolId,
      })()
    ).pipe(
      catchError(error => {
        console.error('Error getting credentials:', error);
        return throwError(error);
      })
    );
  }

  configureAWS(credentials: any) {
    AWS.config.update({
      accessKeyId: credentials.accessKeyId,
      secretAccessKey: credentials.secretAccessKey,
      sessionToken: credentials.sessionToken,
      region: this.region,
    });
    console.log('AWS Config updated with new credentials');
  }

  async getSecretValue(secretName: string): Promise<any> {
    try {
      const credentials = await firstValueFrom(this.getCredentials());
      this.configureAWS(credentials);

    } catch (error) {
      console.error('Error retrieving secret:', error);
      throw error;
    }
  }
}
