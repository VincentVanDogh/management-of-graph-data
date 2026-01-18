export interface PropertyGraphRelation {
  a: any;
  r: any;
  b: any;
  aName: string;
  bName: string;
}

export interface Neo4jNode {
  id: string | number;
  [key: string]: any;
}

export interface Neo4jRelationship {
  id: string | number;
  source: string | number;
  target: string | number;
  [key: string]: any;
}

export interface CytoscapeElement {
  data: {
    id: string;
    source?: string;
    target?: string;
    [key: string]: any;
  };
}

export interface NodeData {
  id: string;
  [key: string]: any; // other properties
}

export interface RelationData {
  id: string;
  source: string;
  target: string;
  [key: string]: any; // other properties
}

export interface CypherResultRecord {
  n?: NodeData;
  m?: NodeData;
  r?: RelationData;
}
