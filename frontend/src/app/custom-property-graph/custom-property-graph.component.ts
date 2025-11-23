import { AfterViewInit, Component } from '@angular/core';
import cytoscape from 'cytoscape';

// TODO: Replace with a GET request
import communities from '../../assets/communities.json';
// import communities from './assets/communities.json';

@Component({
  selector: 'app-custom-property-graph',
  templateUrl: './custom-property-graph.component.html',
  styleUrls: ['./custom-property-graph.component.scss']
})
export class CustomPropertyGraphComponent implements AfterViewInit {

  async ngAfterViewInit() {
    // Load JSON data from assets folder (you can also import or fetch)
    /*
    const response = await fetch('./assets/communities.json');
    const data = await response.json();
     */

    const data = communities as any;

    console.log(data);

    // Convert to cytoscape elements format
    const elements = [
      ...data.nodes.map((node: any) => ({
        data: {id: node.id, label: node.label, ...node}
      })),
      ...data.edges.map((edge: any) => ({
        data: {id: edge.id, source: edge.source, target: edge.target, label: edge.label, ...edge}
      })),
    ];

    cytoscape({
      container: document.getElementById('cy')!,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#007ACC',
            'label': 'data(name)', // adjust accordingly
            'color': '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': 12,
            'width': 30,
            'height': 30,
            'text-wrap': 'wrap'
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#888',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#888',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': 10,
            'text-rotation': 'autorotate',
            'color': '#555'
          }
        }
      ],
      layout: {name: 'cose'}
    });
  }
}
