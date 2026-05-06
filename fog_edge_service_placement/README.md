# Service Placement and Node Allocation in Fog/Edge Computing

This repository contains implementations and results related to heuristic and optimization-based strategies for service placement and computational node allocation in fog and edge computing environments.

The work is structured around three main objectives:

- **Minimizing the number of allocated nodes**
- **Minimizing residual computational resources**
- **Minimizing end-to-end communication hops**

These objectives are addressed through Integer Linear Programming (ILP) models and corresponding heuristic solutions.

---

## 📁 Repository Structure

.
├── data/                      # Input datasets: topologies and application configurations
├── graphs/                    # Jupyter notebooks for visualization and result analysis
├── logs/                      # Execution logs for ILP models and heuristics
├── results/                   # Output files (allocations, metrics, execution times)
├── *.py                       # Heuristic and ILP-based Python scripts
├── get_data.py                # Utility functions to load and preprocess input data
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation

---

## ⚙️ Components

### 🧠 Heuristic Algorithms

- `h1_min_nodes_alloc.py`: Heuristic for minimizing the number of allocated nodes.
- `h2_min_residual.py`: Heuristic for minimizing residual resources.
- `h3_min_hops.py`: Heuristic for minimizing communication hops.

The formal pseudocode of each heuristic is documented in:

- [`docs/heuristic_H1.md`](docs/heuristic_H1.md) — *Node minimization (H-1)*  
- [`docs/heuristic_H2.md`](docs/heuristic_H2.md) — *Residual resource minimization (H-2)*  
- [`docs/heuristic_H3.md`](docs/heuristic_H3.md) — *Hop minimization (H-3)*  

### 📐 ILP-Based Models (Pyomo + Gurobi)

- `m1_min_nodes_alloc_pyomo.py`: ILP model to minimize allocated nodes.
- `m2_min_residual_pyomo.py`: ILP model to minimize residual capacity.
- `m3_min_hops_pyomo.py`: ILP model to minimize network hops.

> All ILP models are implemented using [Pyomo](http://www.pyomo.org/) and solved with [Gurobi Optimizer](https://www.gurobi.com/). Ensure that Gurobi is properly installed and licensed on your machine.

---

## 📊 Visualization and Analysis

Notebooks in the `graphs/` directory:

- `plot_topologies.ipynb`: Visualizes node-link structures.
- `plot_graphs.ipynb`: Compares heuristic and ILP results.
- `plot_flow_placement.ipynb`: Shows flow-based service allocation.
- `result_data_analyze_times.ipynb`: Analyzes execution time and decision efficiency.

---

## 📂 Data

### Input

- **Topologies**: Located in `data/topologies/`, including Germany and Synthetic network scenarios.
- **Applications**: Located in `data/applications/`, with varied microservice pipelines and resource requirements.

### Output

- **Placement Results**: CSV files in `results/` with allocation and performance metrics for each model/heuristic.
- **Execution Logs**: Detailed logs per run stored in `logs/`.

---

## 🔧 Setup

Install dependencies:

```bash
pip install -r requirements.txt

Required packages include:
	•	numpy, pandas
	•	networkx
	•	matplotlib, seaborn
	•	pyomo
	•	gurobipy (must be installed separately and requires a valid Gurobi license)

python h1_min_nodes_alloc.py

python m1_min_nodes_alloc_pyomo.py

Notes
	•	All heuristics are designed to operate on a per-application basis.
	•	The get_data.py module is responsible for reading, normalizing, and returning structured inputs.
	•	Execution times and results may vary depending on the size of the application and the topology.
	•	For ILP execution, ensure Gurobi is installed and licensed correctly.