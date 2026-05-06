import sys
sys.path.append('modules')

import pandas as pd
import numpy as np
import random as rd
import time
import csv
import os

import get_dataH4 as gd

topology = 'Total_Nodes'
path     = 'app_json'
columns  = ['id', 'cpu', 'memory', 'storage', 'bandwidth']
cp       = 1.0

np.set_printoptions(suppress=True)

# ─── Load node data ───────────────────────────────────────────────────────────
def get_data_nodes():
    df_nodes = gd.get_topology_energy(topology, capacity_percent=cp)
    df_nodes = df_nodes[['id', 'cpu', 'memory', 'storage', 'bandwidth', 'p_idle', 'p_max']].reset_index(drop=True)
    df_nodes['id'] = range(len(df_nodes))  # ← replace N01, N02... with 0,1,2...
    return df_nodes

# ─── Load application data ────────────────────────────────────────────────────
def get_data_application(app_file, path):
    df_services = gd.get_application(app_file, path)
    services = df_services[columns].reset_index(drop=True)
    services['id'] = range(len(services))
    return services

# ─── Heuristic H4 ────────────────────────────────────────────────────────────
def get_allocation_energy(nodes_data, services_data, p_idle_list, p_max_list):
    NUM_RUNS  = 100
    n_services = len(services_data)
    maxiter    = 10 * n_services
    half_iter  = maxiter // 2

    energy_list      = []
    time_list        = []
    best_energy      = None
    best_allocations = []
    no_improve_count = 0

    for run in range(NUM_RUNS):
        start_time = time.time()

        services = [[int(v) for v in row] for row in services_data]
        nodes    = [[int(v) for v in row] for row in nodes_data]

        # Sort services by CPU demand descending
        services = sorted(services, key=lambda s: s[1], reverse=True)

        # Shuffle nodes for diversity across runs
        node_order = list(range(len(nodes)))
        rd.shuffle(node_order)
        nodes = [nodes[i] for i in node_order]

        # Rebuild power lists in shuffled order
        p_idle = [p_idle_list[node_order[j]] for j in range(len(nodes))]
        p_max  = [p_max_list [node_order[j]] for j in range(len(nodes))]

        allocations   = []
        allocated_set = set()
        feasible      = True

        # ── Greedy placement loop ─────────────────────────────────────────────
        for service in services:
            s_id   = service[0]
            s_cpu  = service[1]
            s_mem  = service[2]
            s_stor = service[3]
            s_bw   = service[4]

            best_node_idx = None
            best_delta_e  = float('inf')
            best_residual = -1

            for j, node in enumerate(nodes):
                n_cpu  = node[1]
                n_mem  = node[2]
                n_stor = node[3]
                n_bw   = node[4]

                if s_cpu <= n_cpu and s_mem <= n_mem and s_stor <= n_stor and s_bw <= n_bw:
                    cpu_fraction = s_cpu / nodes_data[node_order[j]][1]
                    dynamic_gain = (p_max[j] - p_idle[j]) * cpu_fraction

                    if j in allocated_set:
                        delta_e = dynamic_gain
                    else:
                        delta_e = p_idle[j] + dynamic_gain

                    residual = n_cpu - s_cpu
                    if (delta_e < best_delta_e) or \
                       (delta_e == best_delta_e and residual > best_residual):
                        best_delta_e  = delta_e
                        best_node_idx = j
                        best_residual = residual

            if best_node_idx is None:
                feasible = False
                break

            nodes[best_node_idx][1] -= s_cpu
            nodes[best_node_idx][2] -= s_mem
            nodes[best_node_idx][3] -= s_stor
            nodes[best_node_idx][4] -= s_bw
            allocated_set.add(best_node_idx)
            allocations.append([s_id, nodes[best_node_idx][0]])

        if not feasible:
            time_list.append(time.time() - start_time)
            energy_list.append(float('inf'))
            continue

        # ── Compute total energy for this run ─────────────────────────────────
        total_energy = sum(
            p_idle[j]
            + (p_max[j] - p_idle[j])
              * ((nodes_data[node_order[j]][1] - nodes[j][1]) / nodes_data[node_order[j]][1])
            for j in allocated_set
        )

        energy_list.append(total_energy)
        time_list.append(time.time() - start_time)

        if best_energy is None or total_energy < best_energy:
            best_energy      = total_energy
            best_allocations = allocations
            no_improve_count = 0
        else:
            no_improve_count += 1

        if no_improve_count >= half_iter:
            break

    valid_energies = [e for e in energy_list if e != float('inf')]
    min_energy  = min(valid_energies)        if valid_energies else None
    mean_energy = float(np.mean(valid_energies)) if valid_energies else None
    std_energy  = float(np.std(valid_energies))  if valid_energies else None
    mean_time   = float(np.mean(time_list))

    return min_energy, mean_energy, std_energy, mean_time, best_allocations

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    nodes       = get_data_nodes()
    nodes_data  = nodes[['id', 'cpu', 'memory', 'storage', 'bandwidth']].to_numpy().astype('int')
    p_idle_list = nodes['p_idle'].tolist()
    p_max_list  = nodes['p_max'].tolist()

    results_summary = []

    app_files = sorted([
        f.replace('.json', '')
        for f in os.listdir(f'data/applications/{path}')
        if f.endswith('.json')
    ])

    print('Solving on topology:', topology)
    for app_file in app_files:
        services      = get_data_application(app_file, path)
        services_data = services.to_numpy().astype('int')

        print(f'Allocation to {app_file} with {len(services)} services')

        min_e, mean_e, std_e, mean_t, best_alloc = get_allocation_energy(
            nodes_data, services_data, p_idle_list, p_max_list
        )

        print(f'  Min energy  : {min_e:.4f} W')
        print(f'  Mean energy : {mean_e:.4f} W')
        print(f'  Std energy  : {std_e:.4f} W')
        print(f'  Avg time    : {mean_t:.8f} s')
        print('-' * 40)

        results_summary.append([app_file, min_e, mean_e, std_e, mean_t, best_alloc])

    os.makedirs('results', exist_ok=True)
    with open(f'results/h4_energy_alloc_{topology}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Application', 'MinEnergy_W', 'MeanEnergy_W',
                         'StdEnergy_W', 'MeanTime_s', 'BestAllocations'])
        for row in results_summary:
            writer.writerow(row)

    print('\nSummary:')
    for row in results_summary:
        print(f'{row[0]} | MinE: {row[1]:.2f}W | MeanE: {row[2]:.2f}W | '
              f'Std: {row[3]:.2f} | Time: {row[4]:.8f}s')

if __name__ == '__main__':
    main()