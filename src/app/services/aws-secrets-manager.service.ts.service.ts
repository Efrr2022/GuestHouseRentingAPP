import { Injectable } from '@angular/core';
import { from, throwError, firstValueFrom } from 'rxjs';
import { switchMap, catchError } from 'rxjs/operators';
import { CognitoIdentityClient } from '@aws-sdk/client-cognito-identity';
import { fromCognitoIdentityPool } from '@aws-sdk/credential-provider-cognito-identity';
import AWS from 'aws-sdk';
import {
  SecretsManagerClient,
  GetSecretValueCommand,
  GetSecretValueCommandOutput,
} from '@aws-sdk/client-secrets-manager';

@Injectable({
  providedIn: 'root',
})
export class AwsSecretsManagerService {
  private identityPoolId = 'us-east-1:8c34b8e9-bfea-4d1d-9e99-4c785e150bf8'; // Replace with your Identity Pool ID
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
    console.log(credentials)
    console.log('AWS Config updated with new credentials');
  }

  async getSecretValue(secretName: string): Promise<any> {
    try {
      const credentials = await firstValueFrom(this.getCredentials());
      this.configureAWS(credentials);
      // Create SecretsManagerClient with the obtained credentials
      const client = new SecretsManagerClient({
        region: this.region,
        credentials: {
          accessKeyId: credentials.accessKeyId,
          secretAccessKey: credentials.secretAccessKey,
          sessionToken: credentials.sessionToken,
        }
      });
      
      const command = new GetSecretValueCommand({ SecretId: secretName });
      const response: GetSecretValueCommandOutput = await client.send(command);

      if (response.SecretString) {
        console.log("Number One")
        return JSON.parse(response.SecretString);
      } else if (response.SecretBinary) {
        console.log("Number two")
        const buff = Buffer.from(response.SecretBinary as Uint8Array);
        return JSON.parse(buff.toString('ascii'));
      } else {
        console.log("Number three")
        throw new Error("SecretString and SecretBinary are both undefined");
      }
    } catch (error) {
      console.error('Error retrieving secret:', error);
      throw error;
    }
  }
}
