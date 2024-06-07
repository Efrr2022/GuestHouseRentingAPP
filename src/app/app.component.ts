import { RouterOutlet } from '@angular/router';
import { Component, OnInit } from '@angular/core';
import { S3Client, ListBucketsCommand } from '@aws-sdk/client-s3';
import { AwsSecretsManagerService } from '../app/services/aws-secrets-manager.service.ts.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'CognitoAuth';

  constructor(private secretManager: AwsSecretsManagerService) {}

  async ngOnInit() {
    try {
      const secret = await this.secretManager.getSecretValue('dev/rentalHouseApp');
      console.log('Retrieved secret:', secret);
    } catch (error) {
      console.error('Error retrieving secret:', error);
    }
  }
}
