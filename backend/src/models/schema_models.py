from pydantic import BaseModel
from typing import List, Optional


class NodeType(BaseModel):
    label: str
    csvFileName: str
    idColumn: str
    properties: List[str]


class GeneratedNodeType(BaseModel):
    label: str
    csvFileName: str
    sourceColumn: str
    idStrategy: str = "AUTO"   # future-proof


class EdgeType(BaseModel):
    type: str
    csvFileName: str

    startNodeLabel: str
    startIdColumn: str

    # either direct node OR generated node
    endNodeLabel: Optional[str] = None
    endGeneratedNodeLabel: Optional[str] = None
    endGeneratedFromColumn: Optional[str] = None


class DatasetSchema(BaseModel):
    datasetName: str
    nodeTypes: List[NodeType]
    generatedNodeTypes: List[GeneratedNodeType] = []
    edgeTypes: List[EdgeType]
