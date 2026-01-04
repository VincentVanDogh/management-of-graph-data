export interface NodeSchema {
  idColumn: string | null;
  label: string;
  properties: string[];
}

export interface EdgeSchema {
  startIdColumn: string | null;
  endIdColumn: string | null;
  label: string;
  properties: string[];
}

export interface GraphSchema {
  node: NodeSchema;
  edge: EdgeSchema;
}
