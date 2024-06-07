import { TestBed } from '@angular/core/testing';
import { AwsSecretsManagerService } from './aws-secrets-manager.service.ts.service';


describe('AwsSecretsManagerServiceTsService', () => {
  let service: AwsSecretsManagerService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AwsSecretsManagerService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
