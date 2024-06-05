import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BuyerPageComponent } from './buyer-page.component';

describe('BuyerPageComponent', () => {
  let component: BuyerPageComponent;
  let fixture: ComponentFixture<BuyerPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BuyerPageComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BuyerPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
