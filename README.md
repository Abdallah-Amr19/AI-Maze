# Intelligent Maze Navigation System

An end-to-end AI pathfinding project that demonstrates how a goal-based agent solves a 2D maze using **A\*** graph search with a **Manhattan Distance** heuristic. The application includes a production-style Flask backend, a responsive frontend visualizer, live search animation, random maze generation, custom maze upload, and side-by-side comparison against **BFS**, **DFS**, and **Greedy Best-First Search**.

## Project Overview

This project was designed around a university AI proposal focused on:

- state-space search
- goal-based agents
- heuristic graph search
- open list and closed list management
- shortest path optimization in grid mazes

The maze is modeled as a grid where:

- `0` = open cell
- `1` = wall
- movement is limited to `up`, `down`, `left`, and `right`
- each move has a uniform cost of `1`

The main algorithm is **A\***, which evaluates nodes using:

`f(n) = g(n) + h(n)`

Where:

- `g(n)` is the real cost from the start node to the current node
- `h(n)` is the Manhattan distance estimate from the current node to the goal

## Features

- Random maze generation
- Custom maze upload using `.txt` or `.json`
- Interactive start and goal placement
- Manual wall editing
- Live node expansion visualization
- Final path animation
- Metrics dashboard
- A\*, BFS, DFS, and Greedy Best-First Search support
- Comparison mode for multiple algorithms
- Structured Flask REST API
- Clean modular backend architecture

## Tech Stack

- Frontend: HTML5, CSS3, Vanilla JavaScript
- Backend: Python, Flask
- AI/Search: A\*, BFS, DFS, Greedy Best-First Search
- Data Structures: priority queue (`heapq`), queue, stack, closed set, parent map

## Folder Structure

```text
project/
├── backend/
│   ├── __init__.py
│   ├── app.py
│   ├── requirements.txt
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── astar.py
│   │   ├── base.py
│   │   ├── bfs.py
│   │   ├── dfs.py
│   │   └── greedy.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── maze.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── api.py
│   └── utils/
│       ├── __init__.py
│       ├── maze_generator.py
│       ├── profiler.py
│       └── validation.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
└── README.md
```

## Installation

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
cd "C:\Users\amrbk\Desktop\AI project"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r backend\requirements.txt
```

## Run Instructions

### Start the backend and frontend together

The Flask app serves both the REST API and the frontend UI.

```powershell
python -m backend.app
```

Then open:

- [http://127.0.0.1:5000](http://127.0.0.1:5000)

## API Documentation

### `POST /api/generate-maze`

Generates a random maze.

Request:

```json
{
  "rows": 21,
  "cols": 21,
  "density": 0.2
}
```

Response:

```json
{
  "success": true,
  "maze": {
    "grid": [[1, 1, 1], [1, 0, 1], [1, 0, 0]],
    "start": [1, 1],
    "goal": [2, 2]
  }
}
```

### `POST /api/solve`

Solves the maze using a selected algorithm.

Request:

```json
{
  "grid": [[0, 0, 1], [1, 0, 0], [1, 0, 0]],
  "start": [0, 0],
  "goal": [2, 2],
  "algorithm": "astar"
}
```

Response fields:

- `path`
- `explored_order`
- `found`
- `metrics.path_cost`
- `metrics.expanded_nodes`
- `metrics.generated_nodes`
- `metrics.frontier_peak`
- `metrics.execution_time_ms`
- `metrics.memory_kb`

### `POST /api/compare`

Runs multiple algorithms on the same maze.

Request:

```json
{
  "grid": [[0, 0, 1], [1, 0, 0], [1, 0, 0]],
  "start": [0, 0],
  "goal": [2, 2],
  "algorithms": ["astar", "bfs", "dfs", "greedy"]
}
```

## How the System Works

### Goal-Based Agent

The agent has a clear objective: reach the goal cell from the start cell while respecting maze constraints. It evaluates future moves instead of reacting only to the current cell, which makes it a good fit for search-based planning problems.

### A* Search Internals

1. Insert the start node into the open list.
2. Repeatedly remove the node with the lowest `f(n)`.
3. Run the goal test.
4. Expand valid neighbor cells.
5. Ignore already closed states.
6. Update the parent map and cost values for better paths.
7. Reconstruct the final path when the goal is reached.

### Why Graph Search Avoids Loops

The backend uses a **closed set** to remember visited states. Once a state has been fully expanded, it is not expanded again. This prevents infinite revisits and avoids wasted work on repeated states.

### Manhattan Heuristic

The Manhattan distance is:

`|x1 - x2| + |y1 - y2|`

It is admissible in this project because movement is restricted to horizontal and vertical steps only. It never overestimates the true shortest path in a four-direction grid, so A\* remains optimal.

## Complexity Discussion

- **A\***:
  - Time: worst case exponential in the number of states, but usually much better due to heuristic guidance
  - Space: high, because it stores frontier and visited states
- **BFS**:
  - Time: `O(V + E)`
  - Space: `O(V)`
  - Complete and optimal for equal step costs
- **DFS**:
  - Time: `O(V + E)`
  - Space: `O(V)` in graph search form
  - Not optimal
- **Greedy Best-First Search**:
  - Often fast in practice
  - Not guaranteed to find the shortest path

## Why A* Is Better Than BFS and DFS Here

- It uses domain knowledge through the Manhattan heuristic.
- It still guarantees the optimal shortest path.
- It usually expands fewer nodes than BFS.
- It avoids the poor path quality and deep wandering behavior of DFS.

## Frontend and Backend Communication

- The frontend sends maze data to the backend using `fetch`.
- The backend validates the payload and runs the selected algorithm.
- The backend returns JSON with the exploration order, final path, and metrics.
- The frontend animates the visited nodes first, then animates the final path.

## Screenshots

Add screenshots here after running the project:

- `docs/screenshots/main-dashboard.png`
- `docs/screenshots/astar-run.png`
- `docs/screenshots/comparison-view.png`

## Future Improvements

- Weighted terrain costs
- Diagonal movement support
- Real-time dynamic obstacles
- Exportable run reports
- More advanced comparison charts
- WebSocket-based streaming for very large mazes

## Demo Tips

- Start by generating a maze and explaining the grid representation.
- Show how the start and goal can be moved.
- Run DFS first to show uninformed exploration.
- Then run A\* and compare the smaller explored area.
- Use the comparison panel to discuss optimality, completeness, and heuristic guidance.
