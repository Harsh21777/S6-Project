import sys
import os
import pandas as pd
import numpy as np
import random as rd
import copy
import time
import csv

# Path configuration and global settings
sys.path.append('modules')
np.set_printoptions(suppress=True)

# Global variables
TOPOLOGY = 'germany'
DATA_PATH = 'orign/'
COLUMNS = ['id', 'cpu', 'memory', 'storage', 'bandwidth']
CAPACITY_PERCENT = 1.0  # 100% da capacidade

# Import of custom modules
import get_data as gd  # type: ignore


# ----------------------------------------------------------------------------------

def get_data_nodes(topology, capacity_percent, columns):
    """
    Loads node data, adjusts for the 'melbourne' topology, and removes the base station.
    """
    df_nodes, df_edges = gd.get_topology(topology, capacity_percent=capacity_percent)

    if topology == 'melbourne':
        df_nodes = df_nodes.iloc[1:].reset_index(drop=True)  # Removes the first node (Base Station)
        # For the 'melbourne' topology, all hops are equal to 2
        num_nodes = len(df_nodes)
        hops_matrix = np.full((num_nodes, num_nodes), 2, dtype=int)
        np.fill_diagonal(hops_matrix, 0)  # Distance to itself is 0.
    else:
        graph = gd.create_graph_topology(df_nodes, df_edges)
        hops_matrix = gd.floyd_warshall(graph, weight='hops')

    return df_nodes[columns], df_edges, hops_matrix


def get_data_application(app_name, path, columns):
    """
    Loads service and choreography data for an application.
    """
    df_services, df_choreog = gd.get_application(app_name, path)
    df_services = df_services[columns]
    df_services['id'] = range(len(df_services))  # Reindex service IDs
    return df_services, df_choreog


def prepare_data_for_allocation(nodes, services):
    """
    Prepares node and service data into dictionary format.
    """
    nodes_dict = {i: list(nodes.iloc[i, 1:]) for i in range(len(nodes))}
    services_dict = {i: list(services.iloc[i, 1:]) for i in range(len(services))}
    return nodes_dict, services_dict


# ----------------------------------------------------------------------------------

def count_hops_for_allocations(allocations, hops):
    """
    Counts the total number of hops between the allocated nodes.
    """
    return sum(hops[allocations[i]][allocations[i + 1]] for i in range(len(allocations) - 1))


def find_next_nodes(current_node, hops):
    """
    Finds neighboring nodes based on the hops matrix.
    """
    hop_distances = hops[current_node]
    return sorted([(i, hop_distances[i]) for i in range(len(hop_distances)) if hop_distances[i] > 0], key=lambda x: x[1])


def has_sufficient_resources(service, node):
    """
    Checks if a node has enough resources to allocate the service.
    """
    return all(n >= s for n, s in zip(node, service))


def deduct_resources(node, service):
    """
    Deducts the resources consumed by a service from a node.
    """
    return [n - s for n, s in zip(node, service)]


def allocate_services(services_dict, nodes_dict, hops_matrix):
    """
    Allocates services to nodes while minimizing the number of hops.
    Performs multiple runs to obtain statistics on node usage and time.
    """
    n_exec = 100
    min_hops_list = []
    decision_times = []
    best_allocations = []
    min_hops = float('inf')
    best_nodes_used = None

    for _ in range(n_exec):
        start_time = time.time()
        current_best_allocations = []
        current_min_hops = float('inf')
        allocations = []
        temp_nodes = copy.deepcopy(nodes_dict)
        # Random choice of the initial node for diversification
        starting_node = rd.choice(list(nodes_dict.keys()))
        current_node = starting_node
        for service_id, service in services_dict.items():
            if has_sufficient_resources(service, temp_nodes[current_node]):
                allocations.append(current_node)
                temp_nodes[current_node] = deduct_resources(temp_nodes[current_node], service)
            else:
                next_nodes = find_next_nodes(current_node, hops_matrix)
                next_node = next((n[0] for n in next_nodes if has_sufficient_resources(service, temp_nodes[n[0]])), None)
                if next_node is None:
                    break  # No node available for the service
                current_node = next_node
                allocations.append(current_node)
                temp_nodes[current_node] = deduct_resources(temp_nodes[current_node], service)
        # Execution statistics
        
        decision_times.append(time.time() - start_time)
        if len(allocations) == len(services_dict):
            total_hops = count_hops_for_allocations(allocations, hops_matrix)
            min_hops_list.append(total_hops)
            if total_hops < min_hops:
                min_hops = total_hops
                best_allocations = [(s_id, n_id) for s_id, n_id in zip(services_dict.keys(), allocations)]
                best_nodes_used = len(set(allocations))

    min_hops = min(min_hops_list)
    mean_min_hops = np.mean(min_hops_list)
    std_min_hops = np.std(min_hops_list)
    mean_time = np.mean(decision_times)
    return best_allocations, min_hops, mean_min_hops, std_min_hops, mean_time


# ----------------------------------------------------------------------------------

def main():
    n_exec = 100
    # Loads topology data
    nodes, edges, hops_matrix = get_data_nodes(TOPOLOGY, CAPACITY_PERCENT, COLUMNS)
    allocations_dict = {}

    # Processes allocation for each application
    for app_index in range(20):
        app_name = f'App{app_index}'
        print(f'Processing {app_name}...')
        services, choreography = get_data_application(app_name, DATA_PATH, COLUMNS)
        nodes_dict, services_dict = prepare_data_for_allocation(nodes, services)
        best_allocations, min_hops, mean_min_hops, std_min_hops, mean_time = allocate_services(services_dict, nodes_dict, hops_matrix)
        print(f'Allocations: {best_allocations}')
        print(f'Minimum Hops: {min_hops}')
        print(f'Mean Minimum Hops: {mean_min_hops:.2f}, Std Minimum Hops: {std_min_hops:.2f}, MeanTime: {mean_time:.6f}s\n{"-" * 40}')
        allocations_dict[app_name] = [min_hops, mean_min_hops, std_min_hops, mean_time, best_allocations]

    # Exports results to CSV
    os.makedirs('results', exist_ok=True)
    output_file = f'results/mid/h3_min_hops_{TOPOLOGY}_new.csv'
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Application', 'MinHops', 'MeanMinHops', 'StdMinHops', 'MeanTime', 'BestAllocations'])
        for key, val in allocations_dict.items():
            min_hops, mean_min_hops, std_min_hops, mean_time, best_allocations = val
            writer.writerow([key, min_hops, mean_min_hops, std_min_hops, mean_time, str(best_allocations)])

    print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()