import {Component, OnInit} from '@angular/core';
import cytoscape, { Core } from 'cytoscape';


// TODO: Replace with a GET request
import {CytoscapeElement, PropertyGraphRelation} from "../dtos/property_graph_relation";
import {PropertyGraphService} from "../services/property-graph.service";
import {HttpClient} from "@angular/common/http";
import {EdgeTypeSchema, GraphSchema, NodeTypeSchema} from "../dtos/graph-schema.model";

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

  selectedFiles: CsvFilePreview[] = [];

  datasetName: string = '';

  emptyNodeDraft(): NodeTypeSchema {
    return {
      idColumn: '',
      label: '',
      properties: [],
      csvFileName: ""
    };
  }

  emptyEdgeDraft(): EdgeTypeSchema {
    return {
      startIdColumn: '',
      endIdColumn: '',
      label: '',
      properties: [],
      csvFileName: ""
    };
  }

  // Drafts (what user is currently editing)
  nodeDraft: NodeTypeSchema = this.emptyNodeDraft();
  edgeDraft: EdgeTypeSchema = this.emptyEdgeDraft();

  // Saved schemas
  nodeTypes: NodeTypeSchema[] = [];
  edgeTypes: EdgeTypeSchema[] = [];


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

    Array.from(input.files).forEach(file => {
      if (!file.name.toLowerCase().endsWith('.csv')) return;

      // prevent duplicates
      if (this.selectedFiles.some(f => f.file.name === file.name)) return;

      const reader = new FileReader();

      reader.onload = () => {
        const text = reader.result as string;

        // first row only
        const firstLine = text.split(/\r?\n/)[0];

        // delimiter detection
        const delimiter = firstLine.includes(';') ? ';' : ',';

        const headers = firstLine
          .split(delimiter)
          .map(h => h.trim());

        this.selectedFiles.push({
          file,
          headers
        });
      };

      reader.readAsText(file);
    });

    input.value = '';
  }


  removeFile(index: number) {
    this.selectedFiles.splice(index, 1);
  }

  uploadFilesWithSchema() {
    const schemaPayload = {
      datasetName: this.datasetName,

      nodeTypes: this.nodeTypes.map(n => ({
        label: n.label,
        idColumn: n.idColumn,
        properties: n.properties,
        csvFileName: n.csvFileName
      })),

      edgeTypes: this.edgeTypes.map(e => ({
        startIdColumn: e.startIdColumn,
        endIdColumn: e.endIdColumn,
        properties: e.properties,
        label: e.label,
        csvFileName: e.csvFileName
      }))
    };

    const formData = new FormData();

    // CSV files
    this.selectedFiles.forEach(item => {
      formData.append('files', item.file, item.file.name);
    });

    // Schema JSON
    /*
    formData.append(
      'schema',
      new Blob([JSON.stringify(schemaPayload)], { type: 'application/json' })
    );
     */
    const schemaJson = JSON.stringify(schemaPayload);
    formData.append('schema', schemaJson);


    this.http.post(
      'http://127.0.0.1:8000/schema_datasets',
      formData
    ).subscribe({
      next: res => console.log('Upload success', formData),
      error: err => console.error('Upload failed', formData)
    });
  }


  // Track which CSV file is selected for node and edge
  nodeCsvFileSelected: string | null = null;
  edgeCsvFileSelected: string | null = null;

  // Headers for the selected CSV files
  nodeCsvHeaders: string[] = [];
  edgeCsvHeaders: string[] = []

  // Call this on node CSV file selection change
  onNodeCsvFileSelected(fileName: string) {
    this.nodeCsvFileSelected = fileName;
    const file = this.selectedFiles.find(f => f.file.name === fileName);
    this.nodeCsvHeaders = file ? file.headers : [];

    // Reset nodeDraft columns to avoid stale data
    this.nodeDraft.idColumn = '';
    this.nodeDraft.properties = [];
  }

  // Call this on edge CSV file selection change
  onEdgeCsvFileSelected(fileName: string) {
    this.edgeCsvFileSelected = fileName;
    const file = this.selectedFiles.find(f => f.file.name === fileName);
    this.edgeCsvHeaders = file ? file.headers : [];

    // Reset edgeDraft columns to avoid stale data
    this.edgeDraft.startIdColumn = '';
    this.edgeDraft.endIdColumn = '';
    this.edgeDraft.properties = [];
  }

  addNodeType() {
    if (!this.nodeCsvFileSelected) {
      alert('Please select a CSV file for the node type');
      return;
    }
    if (!this.nodeDraft.idColumn || !this.nodeDraft.label) {
      alert('Node requires ID column and label');
      return;
    }

    this.nodeTypes.push({
      csvFileName: this.nodeCsvFileSelected,
      label: this.nodeDraft.label,
      idColumn: this.nodeDraft.idColumn,
      properties: this.nodeDraft.properties
    });

    this.nodeDraft = this.emptyNodeDraft();
    this.nodeCsvFileSelected = null;
    this.nodeCsvHeaders = [];
  }

  addEdgeType() {
    if (!this.edgeCsvFileSelected) {
      alert('Please select a CSV file for the edge type');
      return;
    }
    if (
      !this.edgeDraft.startIdColumn ||
      !this.edgeDraft.endIdColumn ||
      !this.edgeDraft.label
    ) {
      alert('Edge requires start ID, end ID and label');
      return;
    }

    this.edgeTypes.push({
      csvFileName: this.edgeCsvFileSelected,
      label: this.edgeDraft.label,
      startIdColumn: this.edgeDraft.startIdColumn,
      endIdColumn: this.edgeDraft.endIdColumn,
      properties: this.edgeDraft.properties
    });

    this.edgeDraft = this.emptyEdgeDraft();
    this.edgeCsvFileSelected = null;
    this.edgeCsvHeaders = [];
  }

  get uniqueHeaders(): string[] {
    const headerSet = new Set<string>();
    this.selectedFiles.forEach(f =>
      f.headers.forEach(h => headerSet.add(h))
    );
    return Array.from(headerSet);
  }

  addNodeProperty(column: string) {
    if (!column) return;
    if (!this.nodeDraft.properties.includes(column)) {
      this.nodeDraft.properties.push(column);
    }
  }

  removeNodeProperty(column: string) {
    this.nodeDraft.properties =
      this.nodeDraft.properties.filter(p => p !== column);
  }

  addEdgeProperty(column: string) {
    if (!column) return;
    if (!this.edgeDraft.properties.includes(column)) {
      this.edgeDraft.properties.push(column);
    }
  }

  removeEdgeProperty(column: string) {
    this.edgeDraft.properties =
      this.edgeDraft.properties.filter(p => p !== column);
  }

}
