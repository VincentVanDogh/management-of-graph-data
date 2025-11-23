import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Neo4jPropertyGraphComponent } from './neo4j-property-graph.component';

describe('PropertyGraphComponent', () => {
  let component: Neo4jPropertyGraphComponent;
  let fixture: ComponentFixture<Neo4jPropertyGraphComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ Neo4jPropertyGraphComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Neo4jPropertyGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
