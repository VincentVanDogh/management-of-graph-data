import { AfterViewInit, Component } from '@angular/core';
import cytoscape from 'cytoscape';
import neo4j from 'neo4j-driver';

@Component({
  selector: 'app-neo4j-property-graph',
  template: `<div id="cy" style="width:100%; height:600px;"></div>`,
  styles: []
})
export class Neo4jPropertyGraphComponent implements AfterViewInit {

  async ngAfterViewInit() {
    // Connect to Neo4j
    const driver = neo4j.driver(
      'neo4j://localhost:7687',
      neo4j.auth.basic('neo4j', 'tobias-gacko')
    );

    const session = driver.session();

    try {
      // Run your query
      const result = await session.run(`
        MATCH (n)-[r]->(m)
        RETURN n, r, m LIMIT 50
      `);

      // Prepare Cytoscape elements
      const elements: any[] = [];
      const nodeIds = new Set<string>();

      for (const record of result.records) {
        const n = record.get('n');
        const m = record.get('m');
        const r = record.get('r');

        // Use node property `id` if available, else fallback to internal ID
        const nId = n.properties.id || n.identity.toString();
        const mId = m.properties.id || m.identity.toString();
        const rId = r.identity.toString();

        // Add node n if not already added
        if (!nodeIds.has(nId)) {
          elements.push({
            data: { id: nId, label: n.labels[0], ...n.properties }
          });
          nodeIds.add(nId);
        }

        // Add node m if not already added
        if (!nodeIds.has(mId)) {
          elements.push({
            data: { id: mId, label: m.labels[0], ...m.properties }
          });
          nodeIds.add(mId);
        }

        // Add the edge connecting n -> m
        elements.push({
          data: {
            id: rId,
            source: nId,
            target: mId,
            label: r.type,
            ...r.properties
          }
        });
      }

      // Render the graph with Cytoscape
      cytoscape({
        container: document.getElementById('cy')!,
        elements,
        style: [
          {
            selector: 'node',
            style: {
              'background-color': '#007ACC',
              'label': 'data(name)',       // Adjust if your nodes don't have 'name', consider 'label' or another prop
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
        layout: { name: 'cose' }
      });

    } catch (error) {
      console.error('Neo4j query failed', error);
    } finally {
      await session.close();
      await driver.close();
    }
  }
}
