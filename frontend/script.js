const state = {
    grid: [],
    start: [1, 1],
    goal: [1, 1],
    editMode: "wall",
    animationSpeed: 35,
    isAnimating: false,
    comparisonResults: [],
    activeResult: null,
};

const elements = {
    mazeGrid: document.getElementById("mazeGrid"),
    algorithmSelect: document.getElementById("algorithmSelect"),
    rowsInput: document.getElementById("rowsInput"),
    colsInput: document.getElementById("colsInput"),
    speedInput: document.getElementById("speedInput"),
    speedValue: document.getElementById("speedValue"),
    generateBtn: document.getElementById("generateBtn"),
    solveBtn: document.getElementById("solveBtn"),
    compareBtn: document.getElementById("compareBtn"),
    resetBtn: document.getElementById("resetBtn"),
    modeWallBtn: document.getElementById("modeWallBtn"),
    modeStartBtn: document.getElementById("modeStartBtn"),
    modeGoalBtn: document.getElementById("modeGoalBtn"),
    mazeUploadInput: document.getElementById("mazeUploadInput"),
    statusText: document.getElementById("statusText"),
    metricPathCost: document.getElementById("metricPathCost"),
    metricExpanded: document.getElementById("metricExpanded"),
    metricTime: document.getElementById("metricTime"),
    metricMemory: document.getElementById("metricMemory"),
    metricGenerated: document.getElementById("metricGenerated"),
    metricFrontier: document.getElementById("metricFrontier"),
    comparisonResults: document.getElementById("comparisonResults"),
};

document.addEventListener("DOMContentLoaded", () => {
    bindEvents();
    generateMaze();
});

function bindEvents() {
    elements.generateBtn.addEventListener("click", generateMaze);
    elements.solveBtn.addEventListener("click", solveCurrentMaze);
    elements.compareBtn.addEventListener("click", compareAlgorithms);
    elements.resetBtn.addEventListener("click", resetVisualization);
    elements.speedInput.addEventListener("input", handleSpeedChange);
    elements.modeWallBtn.addEventListener("click", () => setEditMode("wall"));
    elements.modeStartBtn.addEventListener("click", () => setEditMode("start"));
    elements.modeGoalBtn.addEventListener("click", () => setEditMode("goal"));
    elements.mazeUploadInput.addEventListener("change", handleMazeUpload);
}

async function generateMaze() {
    if (state.isAnimating) {
        return;
    }

    setStatus("Generating a new random maze...");

    try {
        const payload = {
            rows: Number(elements.rowsInput.value),
            cols: Number(elements.colsInput.value),
        };
        const response = await apiRequest("/api/generate-maze", payload);
        loadMaze(response.maze);
        setStatus("Maze generated. You can edit cells or run a search algorithm.");
    } catch (error) {
        handleError(error);
    }
}

async function solveCurrentMaze() {
    if (state.isAnimating) {
        return;
    }

    resetCellVisualState();
    setStatus(`Running ${formatAlgorithmName(elements.algorithmSelect.value)}...`);

    try {
        const response = await apiRequest("/api/solve", {
            grid: state.grid,
            start: state.start,
            goal: state.goal,
            algorithm: elements.algorithmSelect.value,
        });
        state.activeResult = response.result;
        await playResult(response.result);
        renderMetrics(response.result.metrics);
        setStatus(buildCompletionMessage(response.result));
    } catch (error) {
        handleError(error);
    }
}

async function compareAlgorithms() {
    if (state.isAnimating) {
        return;
    }

    resetCellVisualState();
    setStatus("Comparing A*, BFS, DFS, and Greedy Best-First Search...");

    try {
        const response = await apiRequest("/api/compare", {
            grid: state.grid,
            start: state.start,
            goal: state.goal,
            algorithms: ["astar", "bfs", "dfs", "greedy"],
        });
        state.comparisonResults = response.results;
        renderComparisonResults(response.results);
        if (response.results.length > 0) {
            state.activeResult = response.results[0];
            await playResult(response.results[0]);
            renderMetrics(response.results[0].metrics);
            setStatus(
                `Comparison complete. Best result: ${formatAlgorithmName(response.results[0].algorithm)}.`
            );
        }
    } catch (error) {
        handleError(error);
    }
}

function loadMaze(maze) {
    state.grid = maze.grid.map((row) => row.slice());
    state.start = maze.start.slice();
    state.goal = maze.goal.slice();
    state.activeResult = null;
    state.comparisonResults = [];
    clearMetrics();
    renderComparisonResults([]);
    renderGrid();
}

function renderGrid() {
    const rows = state.grid.length;
    const cols = state.grid[0].length;
    elements.mazeGrid.innerHTML = "";
    elements.mazeGrid.style.gridTemplateColumns = `repeat(${cols}, minmax(0, 1fr))`;

    state.grid.forEach((row, rowIndex) => {
        row.forEach((cell, colIndex) => {
            const cellElement = document.createElement("button");
            cellElement.type = "button";
            cellElement.className = "maze-cell";
            cellElement.dataset.row = rowIndex;
            cellElement.dataset.col = colIndex;
            cellElement.setAttribute("aria-label", `Cell ${rowIndex}, ${colIndex}`);
            applyBaseCellClass(cellElement, rowIndex, colIndex, cell);
            cellElement.addEventListener("click", () => handleCellClick(rowIndex, colIndex));
            elements.mazeGrid.appendChild(cellElement);
        });
    });
}

function applyBaseCellClass(cellElement, row, col, cellValue) {
    cellElement.className = "maze-cell";

    if (cellValue === 1) {
        cellElement.classList.add("wall");
    }

    if (isSamePosition([row, col], state.start)) {
        cellElement.classList.add("start");
    } else if (isSamePosition([row, col], state.goal)) {
        cellElement.classList.add("goal");
    }
}

function handleCellClick(row, col) {
    if (state.isAnimating) {
        return;
    }

    if (state.editMode === "wall") {
        if (isSamePosition([row, col], state.start) || isSamePosition([row, col], state.goal)) {
            return;
        }
        state.grid[row][col] = state.grid[row][col] === 1 ? 0 : 1;
    } else if (state.editMode === "start") {
        if (state.grid[row][col] === 0 && !isSamePosition([row, col], state.goal)) {
            state.start = [row, col];
        }
    } else if (state.editMode === "goal") {
        if (state.grid[row][col] === 0 && !isSamePosition([row, col], state.start)) {
            state.goal = [row, col];
        }
    }

    resetCellVisualState();
    renderGrid();
}

function setEditMode(mode) {
    state.editMode = mode;
    [elements.modeWallBtn, elements.modeStartBtn, elements.modeGoalBtn].forEach((button) => {
        button.classList.remove("active");
    });

    if (mode === "wall") {
        elements.modeWallBtn.classList.add("active");
    } else if (mode === "start") {
        elements.modeStartBtn.classList.add("active");
    } else {
        elements.modeGoalBtn.classList.add("active");
    }
}

function handleSpeedChange() {
    state.animationSpeed = Number(elements.speedInput.value);
    elements.speedValue.textContent = `${state.animationSpeed} ms`;
}

function resetVisualization() {
    if (state.isAnimating) {
        return;
    }

    resetCellVisualState();
    clearMetrics();
    setStatus("Visualization reset. The maze layout is preserved.");
}

function resetCellVisualState() {
    const cellElements = document.querySelectorAll(".maze-cell");
    cellElements.forEach((cellElement) => {
        const row = Number(cellElement.dataset.row);
        const col = Number(cellElement.dataset.col);
        applyBaseCellClass(cellElement, row, col, state.grid[row][col]);
    });
}

async function playResult(result) {
    state.isAnimating = true;
    resetCellVisualState();

    for (const [row, col] of result.explored_order) {
        if (isSamePosition([row, col], state.start) || isSamePosition([row, col], state.goal)) {
            continue;
        }
        getCellElement(row, col)?.classList.add("explored");
        await sleep(state.animationSpeed);
    }

    if (result.found) {
        for (const [row, col] of result.path) {
            if (isSamePosition([row, col], state.start) || isSamePosition([row, col], state.goal)) {
                continue;
            }
            const cellElement = getCellElement(row, col);
            cellElement?.classList.remove("explored");
            cellElement?.classList.add("path");
            await sleep(Math.max(12, Math.floor(state.animationSpeed * 0.7)));
        }
    }

    state.isAnimating = false;
}

function renderMetrics(metrics) {
    elements.metricPathCost.textContent = metrics.path_cost ?? "No path";
    elements.metricExpanded.textContent = metrics.expanded_nodes;
    elements.metricTime.textContent = `${metrics.execution_time_ms} ms`;
    elements.metricMemory.textContent = `${metrics.memory_kb} KB`;
    elements.metricGenerated.textContent = metrics.generated_nodes;
    elements.metricFrontier.textContent = metrics.frontier_peak;
}

function clearMetrics() {
    elements.metricPathCost.textContent = "-";
    elements.metricExpanded.textContent = "-";
    elements.metricTime.textContent = "-";
    elements.metricMemory.textContent = "-";
    elements.metricGenerated.textContent = "-";
    elements.metricFrontier.textContent = "-";
}

function renderComparisonResults(results) {
    if (!results.length) {
        elements.comparisonResults.className = "comparison-results empty-state";
        elements.comparisonResults.textContent =
            "Comparison results will appear here after running the compare action.";
        return;
    }

    elements.comparisonResults.className = "comparison-results";
    elements.comparisonResults.innerHTML = "";

    results.forEach((result, index) => {
        const card = document.createElement("article");
        card.className = `comparison-card${index === 0 ? " best" : ""}`;
        card.innerHTML = `
            <h3>${formatAlgorithmName(result.algorithm)}</h3>
            <p>Path Cost: ${result.metrics.path_cost ?? "No path"}</p>
            <p>Expanded Nodes: ${result.metrics.expanded_nodes}</p>
            <p>Execution Time: ${result.metrics.execution_time_ms} ms</p>
            <p>Peak Memory: ${result.metrics.memory_kb} KB</p>
        `;

        card.addEventListener("click", async () => {
            if (state.isAnimating) {
                return;
            }
            state.activeResult = result;
            await playResult(result);
            renderMetrics(result.metrics);
            setStatus(`Replaying ${formatAlgorithmName(result.algorithm)} visualization.`);
        });

        elements.comparisonResults.appendChild(card);
    });
}

async function handleMazeUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }

    try {
        const content = await file.text();
        const parsedMaze = parseUploadedMaze(content, file.name);
        loadMaze(parsedMaze);
        setStatus("Custom maze loaded successfully.");
    } catch (error) {
        handleError(error);
    } finally {
        event.target.value = "";
    }
}

function parseUploadedMaze(content, fileName) {
    if (fileName.endsWith(".json")) {
        const parsed = JSON.parse(content);
        validateUploadedMaze(parsed);
        return parsed;
    }

    const lines = content
        .trim()
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean);

    const grid = lines.map((line) =>
        line.split(/\s+/).map((value) => {
            const normalized = Number(value);
            if (![0, 1].includes(normalized)) {
                throw new Error("Text mazes must use only 0 and 1 values.");
            }
            return normalized;
        })
    );

    const maze = {
        grid,
        start: [1, 1],
        goal: [grid.length - 2, grid[0].length - 2],
    };
    validateUploadedMaze(maze);
    return maze;
}

function validateUploadedMaze(maze) {
    if (!Array.isArray(maze.grid) || maze.grid.length === 0) {
        throw new Error("Uploaded maze must include a non-empty grid.");
    }

    const width = maze.grid[0].length;
    maze.grid.forEach((row) => {
        if (!Array.isArray(row) || row.length !== width) {
            throw new Error("Uploaded maze grid must be rectangular.");
        }
        row.forEach((cell) => {
            if (![0, 1].includes(cell)) {
                throw new Error("Maze grid cells must be 0 or 1.");
            }
        });
    });

    if (!Array.isArray(maze.start) || !Array.isArray(maze.goal)) {
        throw new Error("Uploaded maze must include start and goal coordinates.");
    }
}

function getCellElement(row, col) {
    return document.querySelector(`.maze-cell[data-row="${row}"][data-col="${col}"]`);
}

function isSamePosition(first, second) {
    return first[0] === second[0] && first[1] === second[1];
}

function formatAlgorithmName(name) {
    const labels = {
        astar: "A* Search",
        bfs: "Breadth-First Search",
        dfs: "Depth-First Search",
        greedy: "Greedy Best-First Search",
    };
    return labels[name] || name;
}

function buildCompletionMessage(result) {
    if (!result.found) {
        return `${formatAlgorithmName(result.algorithm)} finished without finding a path.`;
    }

    return `${formatAlgorithmName(result.algorithm)} found a path with cost ${result.metrics.path_cost} after exploring ${result.metrics.expanded_nodes} nodes.`;
}

function setStatus(message) {
    elements.statusText.textContent = message;
}

function handleError(error) {
    console.error(error);
    setStatus(error.message || "Unexpected error.");
}

async function apiRequest(url, body) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    });

    const data = await response.json();
    if (!response.ok || !data.success) {
        throw new Error(data.error || "Request failed.");
    }
    return data;
}

function sleep(duration) {
    return new Promise((resolve) => {
        window.setTimeout(resolve, duration);
    });
}
