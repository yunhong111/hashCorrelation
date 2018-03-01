import networkx as nx
import matplotlib.pyplot as plt
from crc8 import crc8
from co_func import append_path
import random
from path_matrix import path_matrix
import mesh_detection as mdt
import mark_flows as mf
from crc32 import crc32
import struct

def get_seeds_table(router_nodes):
    """
    Assign seed and polinmial to node.
    """
    poly_list = (
            [0x31, 0x2f, 0x39, 0xd5, 0x4d, 0x8d, 0x9b, 0x7a, 0x07, 0x49, 0x1d, 0x2d, 0x3d, 0x8b, 0x7b]
    )
    
    np = len(poly_list)   
    seeds = {}
    polys = {}
    i = 0
    
    for node in router_nodes:
        seeds[node] = i*7
        if i < np:
            polys[node] = poly_list[i]
        else:
            k = random.randint(0, np-1)
            polys[node] = poly_list[k]
        i += 1
    
    polys = ({'s3': 0x31, 's4': 0x2f, 's5': 0x39, 
        's6': 0xd5, 's7': 0x4d, 's8': 0x8d, 
        's10': 0x9b, 's11': 0x7a, 's1': 0x07, 
        's2': 0x07, 's9': 0x07, 's12': 0x07}
    )
    
    return seeds, polys

def set_correlation(r1, r2, polys):
    poly_r2 = polys[r2]
    polys[r2] = polys[r1]
    return poly_r2

def reset_correlation(r2, polys, poly):
    polys[r2] = poly
    
def build_graph():
    G = nx.MultiGraph()
    
    edges = ([('s1', 's2', dict(route=0)), ('s1', 's5', dict(route=0)), 
                ('s2', 's3', dict(route=0)), ('s3', 's4', dict(route=0)), 
                ('s3', 's6', dict(route=0)), ('s4', 's5', dict(route=0)), 
                ('s4', 's7', dict(route=0)), ('s4', 's8', dict(route=0)), 
                ('s5', 's6', dict(route=0)), ('s6', 's7', dict(route=0)), 
                ('s6', 's8', dict(route=0)), ('s7', 's8', dict(route=0)), 
                ('s7', 's11', dict(route=0)), ('s8', 's10', dict(route=0)), 
                ('s9', 's10', dict(route=0)), ('s9', 's11', dict(route=0)), 
                ('s10', 's11', dict(route=0)), ('s10', 's12', dict(route=0)), 
                ('s11', 's12', dict(route=0)), 
            ]
    )
    
    host_switch = ([('s1', 'h1', dict(route=0)), ('s2', 'h2', dict(route=0)), 
                    ('s3', 'h3', dict(route=0)), ('s4', 'h4', dict(route=0)), 
                    ('s5', 'h5', dict(route=0)), ('s6', 'h6', dict(route=0)), 
                    ('s7', 'h7', dict(route=0)), ('s8', 'h8', dict(route=0)), 
                    ('s9', 'h9', dict(route=0)), ('s10', 'h10', dict(route=0)), 
                    ('s11', 'h11', dict(route=0)), ('s12', 'h12', dict(route=0))
                ]
    )
    
    G.add_edges_from(edges)
    G.add_edges_from(host_switch)
    return G

def routing(s, d, table):
    paths = list(nx.all_shortest_paths(G, s, d))
    
    for path in paths:
        for i, node in enumerate(path):
            if i < len(path) - 1:
                if d not in table[node]:
                    table[node][d] = []
                if path[i+1] not in table[node][d]:
                    table[node][d].append(path[i+1])
        
def all_routing(G, switch_nodes):
    # Routing table
    table = {}
    for s in G.nodes():
        if 's' in s:
            table[s] = {}
    for s in switch_nodes:
        for d in switch_nodes:
            if s != d:
                routing(s, d, table)
    return table

# No marking packets
def next_hop(cur_hop, pre_hop, s, d, hash_str, 
            table, seeds, polys, flow_paths
        ):
    print('cur_hop, pre_hop', cur_hop, pre_hop)
    if cur_hop == d:
        hash_str0 = hash_str
        hash_str = hash_str0[0:14]
        marker = hash_str0[14:]
        if marker != 'None':
            append_path(hash_str, pre_hop, cur_hop, flow_paths)
        return 
    n = len(hash_str)
    
    # Header = 4+4+2+2+1 bytes
    hash_str0 = hash_str
    hash_str = hash_str0[0:13]
    marker = hash_str0[13:]
    
    if marker == cur_hop:
        append_path(hash_str, pre_hop, cur_hop, flow_paths)
        
    nhop = table[cur_hop][d][0]
    n = len(table[cur_hop][d])
    if n > 1:
        ni = crc8(seeds[cur_hop], hash_str, polys[cur_hop])%n
        nhop = table[cur_hop][d][ni]
    next_hop(nhop, cur_hop, s, d, hash_str0, table, seeds, polys, flow_paths)

def map_addr_int(s, d):
    """
    Map the current source and dest address to the ones in the topo
    """
    
    s_out, d_out = crc32(s), crc32(d)
    return s_out, d_out
    
def map_addr(s, d):
    """
    Map the current source and dest address to the ones in the topo
    """
    s_out, d_out = crc8(0, s, 0x31)%11 + 1, crc8(0, d, 0x1d)%11 + 1
    count = 0
    while s_out == d_out and count < 5:
        s_out, d_out = crc8(0, s, 0x31)%11 + 1, crc8(0, d, 0x1d)%11 + 1
        count += 1
    s_out, d_out = 's' + str(s_out), 's' + str(d_out)
    return s_out, d_out

def map_addr_tree(s, d, tors):
    """
    Map the current source and dest address to the ones in the topo
    """
    n = len(tors)
    s_out, d_out = crc8(0, s, 0x31)%n + 1, crc8(0, d, 0x1d)%n + 1
    count = 0
    while s_out == d_out and count < 5:
        s_out, d_out = crc8(0, s, 0x31)%n + 1, crc8(0, d, 0x1d)%n + 1
        count += 1
    s_out, d_out = tors[s_out], tors[d_out]
    return s_out, d_out

def map_port(sp, dp):
    s_out, d_out = crc32(sp) & 0x0000ffff, crc32(dp) & 0x0000ffff
    return s_out, d_out

def hashStr(data):
    """
    Return the packet header
    """
    s, d = map_addr_int(data[2], data[3])  
    sp, dp = map_port(data[4], data[5])  

    data[2], data[3] = struct.pack('>I', s), struct.pack('>I', d)
    data[4], data[5] = struct.pack('>I', sp)[2:], struct.pack('>I', dp)[2:]
    data[6] = struct.pack('>I', int(data[6]))[-1]
    hash_str = (data[2]
            + data[3]
            + data[4]
            + data[5]
            + data[6]
    )
    return hash_str
    
def flow_routing(file_name, seeds, polys, flow_paths, switch_nodes, table):
    
    mark_group = mf.mark_group_dest(table)
    count = 0;
    start_time = 0;
    is_update = True
    flow_dict = {}
    
    with open((file_name), 'r') as f:
        for line in f:
            count += 1
            if(count < 25000):
                data = line.split()
              
                # Update start time
                if(is_update):
                    start_time = float((data[0]))
                    is_update = False
                  
                # Monitor every second
                #if (float(data[0]) - start_time) > 1:
                    #is_update = True
                    #print('Greater than 1.')
                    #break
                    
                s, d = map_addr(data[2], data[3]) 
                hash_str = hashStr(data)  
                flow_dict[hash_str] = 1
                count_dict, threshold = {}, 100000
                switch_id = mf.marknum(
                        hash_str, count_dict, threshold, 
                        mark_group[d]
                )
                hash_str += switch_id
                next_hop(
                    s, 'h1', s, d, hash_str, table, seeds, polys, flow_paths
                )
            else:
                print('time', (float(data[0]) - start_time))
                print('Flow num:', len(flow_dict))
                print('pkt count:', count)
                break                
    return
    
def single(r1, r2, pairs, switch_nodes, trues, ests, table):
    
    poly = set_correlation(r1, r2, polys)
    
    flow_paths = {}
    flow_routing(file_name, seeds, polys, flow_paths, switch_nodes, table)
    print(flow_paths)
    eeee
    
    rm = path_matrix(flow_paths, switch_nodes)
    print((rm))
    eee
    
    cherns = {}
    dss = []
    for s in switch_nodes:
        cherns[s], ds = mdt.hash_biased(s, rm, switch_nodes, table[s])
        dss.append(ds)
    print('cherns', cherns)
    
    epsilon = 0.001
    for s in switch_nodes:
        if cherns[s] < epsilon:
            trues += 1
            print('++++++++++, s, chern, r1, r2', s, cherns[s], r1, r2)
            pairs.append([r1, r2, cherns[s]])
            ranking = locate_corr(s, rm, switch_nodes, table)
            print('ranking', ranking)
            if len(ranking) != 0:
                if ranking[0][0] == r1 or ranking[0][0] == r2:
                    ests += 1
            
    reset_correlation(r2, polys, poly)
    return trues, ests

def locate_corr(s, rm, switch_nodes, table):
    #
    pre_hops = [x for x in switch_nodes if x != s]
    print('pre_hops', pre_hops)
    cherns = mdt.corr_group(pre_hops, s, rm, switch_nodes, table)
    return cherns

if __name__ == "__main__":
    
    # Build a graph
    G = build_graph()
    
    switch_nodes = ['s' + str(i) for i in range(1, 13)]
       
    # Get the routing path of all nodes
    table = all_routing(G, switch_nodes)
    
    seeds, polys = get_seeds_table(switch_nodes)
    
    file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                + "split_flows_150s_web_sort_host"
    )
    file_name = '/home/yunhong/Research_4/caida_trace/outputs/results'
    single_nodes = ['s1', 's2', 's9', 's12']
    multi_nodes = [x for x in switch_nodes if x not in single_nodes]
    
    pairs = []
    trues, ests = 0, 0
    for r1 in multi_nodes:
        for r2 in multi_nodes:
            if r1 != r2:
                a = 0
                trues, ests = single(
                    r1, r2, pairs, switch_nodes, trues, ests, table
                )
    print('pairs', pairs)
    
    #trues, ests = single('s4', 's3', pairs, switch_nodes, trues, ests)
    print('trues, ests', trues, ests)
    #mdt.corr_group(['s4'], 's3', rm, switch_nodes, table)
    #mdt.corr_group(['s3'], 's4', rm, switch_nodes, table)
    
