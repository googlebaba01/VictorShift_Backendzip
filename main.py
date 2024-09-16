from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Node(BaseModel):
    id: str

class Edge(BaseModel):
    source: str
    target: str

class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

# Route handling POST requests
@app.post('/')
def parse_pipeline(pipeline: Pipeline):
    num_nodes = len(pipeline.nodes)
    num_edges = len(pipeline.edges)

    # Graph construction
    graph = {node.id: [] for node in pipeline.nodes}
    for edge in pipeline.edges:
        if edge.source not in graph or edge.target not in graph:
            raise HTTPException(status_code=400, detail="Invalid edge with non-existent node")
        graph[edge.source].append(edge.target)

    is_dag = not has_cycle(graph)

    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'is_dag': is_dag
    }

# Cycle detection using DFS
def has_cycle(graph):
    visited = set()
    rec_stack = set()

    def visit(node):
        if node in rec_stack:
            return True
        if node in visited:
            return False

        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if visit(neighbor):
                return True

        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            if visit(node):
                return True

    return False
