import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CustomPropertyGraphComponent } from './custom-property-graph.component';

describe('CustomPropertyGraphComponent', () => {
  let component: CustomPropertyGraphComponent;
  let fixture: ComponentFixture<CustomPropertyGraphComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CustomPropertyGraphComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CustomPropertyGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
