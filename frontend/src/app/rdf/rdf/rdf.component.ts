import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-rdf',
  templateUrl: './rdfcomponent.html', // fixed path
  styleUrls: ['./rdf.component.scss']
})
export class RdfComponent implements OnInit {

  rdfData: any;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.loadRdfData();
  }

  loadRdfData() {
  this.http.get('assets/data/research_product.jsonld')
  .subscribe({
    next: (data) => this.rdfData = data,
    error: (err) => console.error('Error loading RDF JSON-LD:', err)
  });
  }

  // Helper function used in template
  isLast(item: any, array: any[]): boolean {
    return array.indexOf(item) === array.length - 1;
  }
}
