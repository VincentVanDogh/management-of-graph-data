import {Component, OnInit} from '@angular/core';
import cytoscape, { Core } from 'cytoscape';


// TODO: Replace with a GET request
import {CypherResultRecord, CytoscapeElement, PropertyGraphRelation} from "../dtos/property_graph_relation";
import {PropertyGraphService} from "../services/property-graph.service";
import {HttpClient} from "@angular/common/http";

@Component({
  selector: 'app-custom-property-graph',
  templateUrl: './custom-property-graph.component.html',
  styleUrls: ['./custom-property-graph.component.scss']
})
export class CustomPropertyGraphComponent implements OnInit {

  transportData: PropertyGraphRelation[] = [];
  cy!: Core;
  // cypherQuery = "MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50";
  cypherQuery = "MATCH (a)-[r:CONNECTED_BY]->(b) RETURN a, r, b, a.halt_lang AS aName, b.halt_lang AS bName LIMIT 500;";

  elements: CytoscapeElement[] = [];
  pastQueries: string[] = [];

  selectedFiles: File[] = [];

  constructor(private service: PropertyGraphService, private http: HttpClient) {
  }

  ngOnInit(): void {
    // Run initial query immediately
    this.executeQuery(this.cypherQuery);

    // Initialize Cytoscape container
    this.cy = cytoscape({
      container: document.getElementById('graphContainer'),
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#0074D9',
            'label': 'data(label)',
            'color': '#000',
            'font-size': '10px'
          }
        },
        {
          selector: 'edge',
          style: {
            'line-color': '#C0C0C0',
            'label': 'data(label)',
            'font-size': '8px',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.5
          }
        }
      ]
    });
  }

  drawGraph(data: PropertyGraphRelation[]): void {
    this.cy = cytoscape({
      container: document.getElementById('graphContainer'),

      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#0074D9',
            'label': 'data(label)',
            'color': '#000',
            'font-size': '10px'
          }
        },
        {
          selector: 'edge',
          style: {
            'line-color': '#C0C0C0',
            'label': 'data(label)',
            'font-size': '8px',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'arrow-scale': 1.5
          }
        }
      ]
    });

    const nodes = new Map();  // prevent duplicates
    const edges: any[] = [];

    data.forEach(rel => {
      // a-node
      if (!nodes.has(rel.a.id)) {
        nodes.set(rel.a.id, {
          data: {id: rel.a.id, label: rel.aName}
        });
      }

      // b-node
      if (!nodes.has(rel.b.id)) {
        nodes.set(rel.b.id, {
          data: {id: rel.b.id, label: rel.bName}
        });
      }

      // edge
      edges.push({
        data: {
          id: `${rel.a.id}-${rel.b.id}-${rel.r.linie}`,
          source: rel.a.id,
          target: rel.b.id,
          label: rel.r.linie
        }
      });
    });

    this.cy.add([...nodes.values(), ...edges]);
    this.cy.layout({
      name: 'cose',
      animate: true
    }).run();
  }

  executeQuery(query: string): void {
    this.service.runCypherQuery(query).subscribe({
      next: (response: any) => {
        console.log(response)
        const results = response.results;
        const elements: CytoscapeElement[] = [];
        const nodesAdded = new Set<string>();

        // Update past queries list
        const queries = response.queries ?? [];
        this.pastQueries = queries.map((q: any) => q.query);

        results.forEach((record: any) => {
          // Handle node a
          if (record.a && !nodesAdded.has(record.a.id)) {
            elements.push({
              data: {
                id: record.a.id,
                label: record.a.halt_lang ?? record.a.id,
              }
            });
            nodesAdded.add(record.a.id);
          }

          // Handle node b if exists
          if (record.b && !nodesAdded.has(record.b.id)) {
            elements.push({
              data: {
                id: record.b.id,
                label: record.b.halt_lang ?? record.b.id,
              }
            });
            nodesAdded.add(record.b.id);
          }

          // Handle relationship r if exists
          if (record.r) {
            elements.push({
              data: {
                id: record.r.id ?? `${record.a.id}-${record.b.id}`,
                source: record.a.id,
                target: record.b.id,
                label: record.r.linie ?? '',
              }
            });
          }
        });

        this.elements = elements;

        if (this.cy) {
          this.cy.elements().remove();
          this.cy.add(this.elements);
          this.cy.layout({ name: 'cose' }).run();
        }
      },
      error: (err) => {
        console.error('Error executing query', err);
      }
    });
  }

  // Logic for uploading CSV-files to the backend:
  onFilesSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (!input.files) return;

    for (let i = 0; i < input.files.length; i++) {
      const file = input.files[i];

      // only CSV
      if (!file.name.toLowerCase().endsWith('.csv')) continue;

      // prevent duplicates (by filename)
      const exists = this.selectedFiles.some(f => f.name === file.name);
      if (!exists) {
        this.selectedFiles.push(file);
      }
    }

    // reset input so same file can be re-selected later if removed
    input.value = '';
  }

  removeFile(index: number) {
    this.selectedFiles.splice(index, 1);
  }

  uploadFiles() {
    const formData = new FormData();

    // IMPORTANT: key must be "file" to match FastAPI
    this.selectedFiles.forEach(file => {
      formData.append('file', file);
    });

    this.http.post('http://127.0.0.1:8000/upload', formData)
      .subscribe({
        next: (res) => {
          console.log('Upload success:', res);
        },
        error: (err) => {
          console.error('Upload failed:', err);
        }
      });
  }


}
