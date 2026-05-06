import sys
sys.path.append('modules')

import pandas as pd
import numpy as np
import pyomo.environ as pyo
from pyomo.environ import *
from pyomo.opt import SolverFactory
import time
import csv
import os

import get_dataM4 as gd

topology = 'Total_Nodes'
path     = 'app_json'
columns       = ['id', 'cpu', 'memory', 'storage', 'bandwidth']
power_columns = ['id', 'cpu', 'memory', 'storage', 'bandwidth', 'p_idle', 'p_max']
cp = 1.0

np.set_printoptions(suppress=True)

# ─── Load node data ───────────────────────────────────────────────────────────
def get_data_nodes():
    try:
        df_nodes = gd.get_topology_energy(topology, capacity_percent=cp)
        df_nodes = df_nodes[power_columns].reset_index(drop=True)
        return df_nodes
    except Exception as e:
        raise RuntimeError(f"Error loading node data: {e}")

# ─── Load application data ────────────────────────────────────────────────────
def get_data_application(app_file, path):
    try:
        df_services = gd.get_application(app_file, path)
        services = df_services[columns].reset_index(drop=True)
        services['id'] = range(len(services))
        return services
    except Exception as e:
        raise RuntimeError(f"Error loading application data {app_file}: {e}")

# ─── ILP Model M4 ────────────────────────────────────────────────────────────
def get_placement(services, nodes):
    qtd_nodes    = len(nodes)
    qtd_services = len(services)

    start_time = time.time()
    model = pyo.ConcreteModel()

    # ── Decision variables ────────────────────────────────────────────────────
    model.x = pyo.Var(range(qtd_services), range(qtd_nodes), domain=Binary)
    model.z = pyo.Var(range(qtd_nodes),    domain=Binary)

    x = model.x
    z = model.z

    # ── Objective: minimize total energy ─────────────────────────────────────
    model.obj = pyo.Objective(
        expr = sum(
            nodes.loc[j, 'p_idle'] * z[j]
            + (nodes.loc[j, 'p_max'] - nodes.loc[j, 'p_idle'])
              * sum(
                    (services.loc[i, 'cpu'] / nodes.loc[j, 'cpu']) * x[i, j]
                    for i in range(qtd_services)
                )
            for j in range(qtd_nodes)
        ),
        sense = minimize
    )

    # ── C1: each service on exactly one node ──────────────────────────────────
    model.con1 = pyo.ConstraintList()
    for i in range(qtd_services):
        model.con1.add(sum(x[i, j] for j in range(qtd_nodes)) == 1)

    # ── C2-C5: resource capacity constraints ──────────────────────────────────
    model.con2 = pyo.ConstraintList()
    model.con3 = pyo.ConstraintList()
    model.con4 = pyo.ConstraintList()
    model.con5 = pyo.ConstraintList()
    for j in range(qtd_nodes):
        model.con2.add(sum(x[i,j] * services.loc[i,'cpu']       for i in range(qtd_services)) <= nodes.loc[j,'cpu'])
        model.con3.add(sum(x[i,j] * services.loc[i,'memory']    for i in range(qtd_services)) <= nodes.loc[j,'memory'])
        model.con4.add(sum(x[i,j] * services.loc[i,'storage']   for i in range(qtd_services)) <= nodes.loc[j,'storage'])
        model.con5.add(sum(x[i,j] * services.loc[i,'bandwidth'] for i in range(qtd_services)) <= nodes.loc[j,'bandwidth'])

    # ── C6: service only on activated node ────────────────────────────────────
    model.con6 = pyo.ConstraintList()
    for i in range(qtd_services):
        for j in range(qtd_nodes):
            model.con6.add(x[i, j] <= z[j] * qtd_services)

    # ── Solve ─────────────────────────────────────────────────────────────────
    opt     = SolverFactory('gurobi', solver_io="python")
    results = opt.solve(model)

    time_placement = '{:.8f}'.format(time.time() - start_time)
    time_solver    = results.solver.wallclock_time

    # ── Extract results ───────────────────────────────────────────────────────
    allocations     = []
    nodes_allocated = []
    for i in range(qtd_services):
        for j in range(qtd_nodes):
            if model.x[i, j]() == 1:
                nodes_allocated.append(j)
                allocations.append((i, j))

    total_energy = model.obj()

    termination = results.solver.termination_condition
    if termination == TerminationCondition.optimal:
        status = 'Optimal'
    elif termination == TerminationCondition.feasible:
        status = 'Feasible'
    else:
        status = 'Infeasible'

    print(f'Total energy (W)  : {total_energy:.4f}')
    print(f'Nodes used        : {sorted(set(nodes_allocated))}')
    print(f'Allocations       : {allocations}')
    print(f'Time placement    : {time_placement} s')
    print(f'Time solver       : {time_solver} s')
    print(f'Status            : {status}')

    return allocations, nodes_allocated, total_energy, time_placement, time_solver, status

# ─── Main ─────────────────────────────────────────────────────────────────────
nodes = get_data_nodes()
dict_allocations = {}

# Get all app json files sorted
app_files = sorted([f.replace('.json', '') for f in os.listdir(f'data/applications/{path}') if f.endswith('.json')])

print('Solving on topology:', topology)
for app_file in app_files:
    services = get_data_application(app_file, path)
    print(f'Allocation to {app_file} with {len(services)} services.')

    allocations, nodes_allocated, total_energy, time_placement, solver_time, status = \
        get_placement(services, nodes)

    dict_allocations[app_file] = (allocations, total_energy, time_placement, solver_time, status)
    print('\n-----------------------------------\n')

# ─── Save results to CSV ──────────────────────────────────────────────────────
os.makedirs('results', exist_ok=True)
with open(f'results/m4_energy_alloc_{topology}.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Application', 'Allocations', 'TotalEnergy_W',
                     'TimePlacement_s', 'TimeSolver_s', 'Status'])
    for key, val in dict_allocations.items():
        writer.writerow([key, val[0], val[1], val[2], val[3], val[4]])