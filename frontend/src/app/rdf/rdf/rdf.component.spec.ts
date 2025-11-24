import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RdfComponent } from './rdf.component';

describe('RdfComponent', () => {
  let component: RdfComponent;
  let fixture: ComponentFixture<RdfComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ RdfComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RdfComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
