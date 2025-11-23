import { AfterViewInit, Component } from '@angular/core';
import cytoscape from 'cytoscape';

// TODO: Replace with a GET request
import communities from '../../assets/communities.json';

@Component({
  selector: 'app-custom-property-graph',
  templateUrl: './custom-property-graph.component.html',
  styleUrls: ['./custom-property-graph.component.scss']
})
export class CustomPropertyGraphComponent implements AfterViewInit {

  private allData: any;
  queryText: string = `MATCH (n)-[r]->(m)\nRETURN n, r, m LIMIT 50`;
  private cy: any;

  async ngAfterViewInit() {
    this.allData = communities;
    this.runQuery();
  }

  onQueryKeydown(event: KeyboardEvent) {
    if ((event.key === 'Enter' && event.shiftKey) || event.key === 'Enter' && event.ctrlKey) {
      event.preventDefault();
      this.runQuery();
    }
  }

  runQuery() {
    const query = this.queryText;

    // Parse LIMIT <number>
    const limitMatch = query.match(/LIMIT\s+(\d+)/i);
    const limit = limitMatch ? parseInt(limitMatch[1], 10) : Infinity;

    // Very simple Cypher-like processor:
    // MATCH (n)-[r]->(m)
    const edges = this.allData.edges.slice(0, limit);
    const nodesUsed = new Set<string>();

    edges.forEach((e: any) => {
      nodesUsed.add(e.source);
      nodesUsed.add(e.target);
    });

    const nodes = this.allData.nodes.filter((n: any) => nodesUsed.has(n.id));

    // Convert to Cytoscape elements
    const elements = [
      ...nodes.map((node: any) => ({
        data: { id: node.id, label: node.label, ...node }
      })),
      ...edges.map((edge: any) => ({
        data: { id: edge.id, source: edge.source, target: edge.target, label: edge.label, ...edge }
      }))
    ];

    // Render graph
    if (this.cy) this.cy.destroy();

    this.cy = cytoscape({
      container: document.getElementById('cy'),
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#007ACC',
            'label': 'data(label)',
            'text-valign': 'top',        // place label ABOVE node
            'text-halign': 'center',
            'text-margin-y': -8,         // move text upward
            'color': '#000',
            'font-size': 12,
            'font-weight': 'bold',
            'width': 25,
            'height': 25
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#555',
            'target-arrow-color': '#555',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': 10,
            'color': '#333'
          }
        }
      ],
      layout: { name: 'cose' }
    });
  }
}
