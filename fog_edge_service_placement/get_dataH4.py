import pandas as pd
import json
import numpy as np
import networkx as nx

def get_topology_energy(net_name, capacity_percent=1.0):
    df_nodes = pd.read_csv('data/topologies/'+net_name+'.csv')

    if 'pidle' not in df_nodes.columns or 'pmax' not in df_nodes.columns:
        raise ValueError(f"{net_name}.csv is missing 'pidle' or 'pmax' columns!")

    df_nodes = df_nodes.rename(columns={
        'node_index' : 'id',
        'cpu_cap'    : 'cpu',
        'bw_cap'     : 'bandwidth',
        'mem_cap'    : 'memory',
        'sto_cap'    : 'storage',
        'pidle'      : 'p_idle',
        'pmax'       : 'p_max'
    })

    df_nodes['cpu']       = df_nodes['cpu']       * capacity_percent
    df_nodes['memory']    = df_nodes['memory']    * capacity_percent
    df_nodes['bandwidth'] = df_nodes['bandwidth'] * capacity_percent

    return df_nodes

def get_application(app_name, base):
    with open('data/applications/'+base+'/'+app_name+'.json', 'r') as f:
        data = json.load(f)

    df_services = pd.DataFrame(data)
    df_services = df_services.rename(columns={
        'service_id'  : 'id',
        'cpu_demand'  : 'cpu',
        'bw_demand'   : 'bandwidth',
        'mem_demand'  : 'memory',
        'sto_demand'  : 'storage'
    })

    return df_services