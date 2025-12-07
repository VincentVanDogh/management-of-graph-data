import { TestBed } from '@angular/core/testing';

import { PropertyGraphService } from './property-graph.service';

describe('PropertyGraphService', () => {
  let service: PropertyGraphService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PropertyGraphService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
