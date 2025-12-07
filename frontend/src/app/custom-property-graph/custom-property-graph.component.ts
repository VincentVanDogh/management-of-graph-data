import {Component, OnInit} from '@angular/core';
import cytoscape, { Core } from 'cytoscape';


// TODO: Replace with a GET request
import communities from '../../assets/communities.json';
import {PropertyGraphRelation} from "../dtos/property_graph_relation";
import {PropertyGraphService} from "../services/property-graph.service";

@Component({
  selector: 'app-custom-property-graph',
  templateUrl: './custom-property-graph.component.html',
  styleUrls: ['./custom-property-graph.component.scss']
})
export class CustomPropertyGraphComponent implements OnInit {

  transportData: PropertyGraphRelation[] = [];
  cy!: Core;

  constructor(private service: PropertyGraphService) {}

  ngOnInit(): void {
    this.service.getTransportData().subscribe(data => {
      this.transportData = data;
      this.drawGraph(data);
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
          data: { id: rel.a.id, label: rel.aName }
        });
      }

      // b-node
      if (!nodes.has(rel.b.id)) {
        nodes.set(rel.b.id, {
          data: { id: rel.b.id, label: rel.bName }
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
}
