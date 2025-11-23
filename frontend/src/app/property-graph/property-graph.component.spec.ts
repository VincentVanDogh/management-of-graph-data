import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PropertyGraphComponent } from './property-graph.component';

describe('PropertyGraphComponent', () => {
  let component: PropertyGraphComponent;
  let fixture: ComponentFixture<PropertyGraphComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ PropertyGraphComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PropertyGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
