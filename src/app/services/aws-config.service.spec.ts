import { TestBed } from '@angular/core/testing';

import { AwsConfigService } from './aws-config.service';

describe('AwsConfigService', () => {
  let service: AwsConfigService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AwsConfigService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
