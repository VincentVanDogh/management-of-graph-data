export interface NodeTypeSchema  {
  idColumn: string | null;
  label: string;
  properties: string[];
  csvFileName: string;
}

export interface EdgeTypeSchema  {
  startIdColumn: string | null;
  endIdColumn: string | null;
  label: string;
  properties: string[];
  csvFileName: string;
}

export interface GraphSchema {
  node: NodeTypeSchema;
  edge: EdgeTypeSchema ;
}
