from typing import Dict, Optional
import uuid
from enum import Enum

class NodeRelationship(str, Enum):
    PREVIOUS = "previous"
    NEXT = "next"

class RelatedNodeInfo:
    def __init__(self, node_id: str):
        self.node_id = node_id

class TextNode:
    def __init__(self, text: str):
        self.text = text
        self.node_id = str(uuid.uuid4())
        self.relationships: Dict[NodeRelationship, RelatedNodeInfo] = {}