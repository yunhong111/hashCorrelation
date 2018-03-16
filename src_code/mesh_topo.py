import networkx as nx
import matplotlib.pyplot as plt
from crc8 import crc8
import co_func as cf
from co_func import append_path, collect_flows
import random
from path_matrix import path_matrix
import mesh_detection_flow_table as mdt
import mark_flows as mf
from crc32 import crc32
import struct
import application as ap
import pandas as pd
import operator
import topo as tp
import json
import os.path
from collections import Counter
import sys

def set_correlation(r1, r2, polys):
    """
    Make the two switches use the same hash polinomials
    """
    
    poly_r2 = polys[r2]
    polys[r2] = polys[r1]
    return poly_r2

def reset_correlation(r2, polys, poly):
    """
    Recover the polynomial on the switch
    """
    
    polys[r2] = poly
    
def build_graph(edges):
    """
    Build the graph by the given topology
    """
    
    G = nx.MultiGraph()
    G.add_edges_from(edges)
    return G

def routing(G, s, d, table):
    """
    Build routing table based on shortest path for the s,d pair
    """
    
    try:
        paths = list(nx.all_shortest_paths(G, s, d))
    except:
        print('s, d', s, d)
        paths = []
        print('nx.has_path(G, s, d)', nx.has_path(G, s, d))
        eee
    #print('len(paths)', len(paths))    
    for path in paths:
        for i, node in enumerate(path):
            if i < len(path) - 1:
                if node not in table:
                    table[node] = {}
                if d not in table[node]:
                    table[node][d] = []
                if path[i+1] not in table[node][d]:
                    table[node][d].append(path[i+1])
        
def all_routing(G, switch_nodes, table_file_name):
    """
    Build routing table for all the s,d pairs
    """

    table = {}
    for s in switch_nodes:
        for d in switch_nodes:
            if s != d:
                routing(G, s, d, table)

    with open(table_file_name, 'w') as file:
        file.write(json.dumps(table))

    return table

def all_routing_tree(G, tors, table_file_name):
    """
    Build routing table for all the s, d pairs from Tors to Tors
    """
    
    table = {}
    for s in G.nodes():
        table[s] = {}
    for s in tors:
        for d in tors:
            if s != d:
                routing(G, s, d, table)

    with open(table_file_name, 'w') as file:
        file.write(json.dumps(table))
    return table
    
def all_routing_tree_2(G, tors1, tors2, table_file_name):
    """
    Build routing table for all the s, d pairs from Tors to Tors
    """
    
    table = {}
    for s in G.nodes():
        table[s] = {}
    for s in tors1:
        for d in tors2:
            if s != d:
                routing(G, s, d, table)
    for d in tors1:
        for s in tors2:
            if s != d:
                routing(G, s, d, table)

    with open(table_file_name, 'w') as file:
        file.write(json.dumps(table))
    return table

# No marking packets
def next_hop(cur_hop, pre_hop, s, d, hash_str, size,
            table, seeds, polys, flow_paths, cflow_dict, app_link_dict, select_dict={}
    ):
            
    if cur_hop == d:
        hash_str0 = hash_str
        hash_str = hash_str0[0:14]
        marker = hash_str0[14:]
        if marker == cur_hop:
            append_path(hash_str, pre_hop, cur_hop, d, flow_paths)
            select_dict[hash_str] = 1
        return 
    n = len(hash_str)
    
    # Header = 4+4+2+2+1 bytes
    hash_str0 = hash_str
    hash_str = hash_str0[0:13]
    marker = hash_str0[13:]
    
    collect_flows(hash_str, pre_hop, cur_hop, size, cflow_dict)
    if marker == cur_hop:
        append_path(hash_str, pre_hop, cur_hop, d, flow_paths)
        select_dict[hash_str] = 1
        
    nhop = table[cur_hop][d][0]
    n = len(table[cur_hop][d])
    if n > 1:
        ni = crc8(seeds[cur_hop], hash_str, polys[cur_hop])%n
        nhop = table[cur_hop][d][ni]
    next_hop(
        nhop, cur_hop, s, d, hash_str0, size, table, seeds, polys, 
        flow_paths, cflow_dict, app_link_dict, select_dict
    )

# No marking packets
def next_hop_rand_mark(cur_hop, pre_hop, s, d, hash_str, size,
            table, seeds, polys, flow_paths, 
            cflow_dict, app_link_dict, app_link_flow_dict, select_dict={},
            drop_id=0, r_threshold=0.0, black_hole='sh41', test_hop='', add_byte_dict = {}
        ):

    if cur_hop == d:
        hash_str0 = hash_str
        hash_str = hash_str0[0:13]
        marker = hash_str0[13:]
        if marker == "1":
            append_path(hash_str, pre_hop, cur_hop, d, flow_paths, size=size)
            #select_dict[hash_str] = 1
        return
    
    # Header = 4+4+2+2+1 bytes
    hash_str0 = hash_str
    hash_str = hash_str0[0:13]
    marker = hash_str0[13:]
    
    next_hops = ''
    if pre_hop in table:
        next_hops = ','.join(sorted(table[pre_hop][d]))
    
    if black_hole != None:
        collect_flows(
            hash_str, pre_hop, cur_hop, size, 
            cflow_dict, app_link_dict, app_link_flow_dict, next_hops, d=s
        )
 
    nhop = table[cur_hop][d][0]
    
    n = len(table[cur_hop][d])
    if n > 1:
        ni = crc8(seeds[cur_hop], hash_str, polys[cur_hop])%n
        nhop = table[cur_hop][d][ni]
        
        if cur_hop == test_hop:
            select_dict[hash_str] = 1
    
    
    # Drop some packets from a particular link
    """if black_hole == nhop and int(int(s[3:])/129) == drop_id:
        r = random.random()
        if r < r_threshold:
            return"""
    # Randomly choosen a flow and add extra byte to it
    if r_threshold > 0 and n > 1 and cur_hop == test_hop and nhop == table[cur_hop][d][0] and len(add_byte_dict) < 3:
        add_byte_dict[hash_str] = 1000*size
        size = 2.0*1024**2
        print 'haha'
    
    if marker == "1":
        append_path(hash_str, pre_hop, cur_hop, d, flow_paths, size=size)
            
    next_hop_rand_mark(
        nhop, cur_hop, s, d, hash_str0, size, table, seeds, polys, 
        flow_paths, cflow_dict, app_link_dict, app_link_flow_dict, select_dict,
        drop_id=drop_id, r_threshold=r_threshold, black_hole=black_hole,
        test_hop=test_hop, add_byte_dict=add_byte_dict
    )

# Using hash set to get the paths of the flows
def next_hop_hash_set(cur_hop, pre_hop, s, d, hash_str, 
            table, seeds, polys, flow_paths, select_dict={}, test_hop = ''
    ):
            
    select_range = 1 << 28        
    if cur_hop == d:
        hash_str0 = hash_str
        hash_str = hash_str0[0:13]
        marker = hash_str0[13:]
        hash_mid = crc32(hash_str)
        if hash_mid < select_range:
            append_path(hash_str, pre_hop, cur_hop, d, flow_paths)
            if cur_hop == test_hop:
                select_dict[hash_str] = 1
        return 
    n = len(hash_str)
    
    # Header = 4+4+2+2+1 bytes
    hash_str0 = hash_str
    hash_str = hash_str0[0:13]
    marker = hash_str0[13:]
    
    hash_mid = crc32(hash_str)
    if hash_mid < select_range:
        append_path(hash_str, pre_hop, cur_hop, d, flow_paths)
        if cur_hop == test_hop:
            select_dict[hash_str] = 1
        
    nhop = table[cur_hop][d][0]
    n = len(table[cur_hop][d])
    if n > 1:
        ni = crc8(seeds[cur_hop], hash_str, polys[cur_hop])%n
        nhop = table[cur_hop][d][ni]
    next_hop_hash_set(
        nhop, cur_hop, s, d, hash_str0, table, seeds, polys, 
        flow_paths, select_dict, test_hop=test_hop
    )

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
    if len(tors) < 2:
        print('map_addr_tree: Error: len(tors) < 2')
        eee
    tors1 = tors[:]  
    n = len(tors)
    #s_out  = crc8(0, s, 0x31)%n + 1
    s_out  = random.randint(0, n-1) + 1
    s_out = tors[s_out-1]
    tors1.remove(s_out)
    #d_out = crc8(0, d, 0x1d)%(n-1) + 1
    d_out  = random.randint(0, n-2) + 1
    d_out = tors1[d_out-1]
    return s_out, d_out

def map_addr_tree_app(s, d, tors):
    """
    Map the current source and dest address to the ones in the topo
    """
    if len(tors) < 2:
        print('map_addr_tree: Error: len(tors) < 2')
        eee
    tors1 = tors[:]  
    n = len(tors)
    s_out  = random.randint(0, n-1) + 1
    s_out = tors[s_out-1]
    tors1.remove(s_out)

    d_out = 'e1'
    return s_out, d_out
    
def map_addr_tree_2(s, d, tors1, tors2):
    """
    Map the current source and dest address to the ones in the topo
    """
    s_d = crc8(0, s, 0x31)%2
    if s_d == 1:
        tors1, tors2 = tors2, tors1
    n1 = len(tors1)
    n2 = len(tors2)
    #s_out, d_out = crc8(0, s, 0x31)%n1 + 1, crc8(0, d, 0x1d)%n2 + 1
    s_out, d_out = random.randint(0, n1-1) + 1, random.randint(0, n2-1) + 1
    s_out, d_out = tors1[s_out-1], tors2[d_out-1]
    return s_out, d_out

def map_addr_tree_3(s, d, tors, block=4):
    """
    Map the current source and dest address to the ones in the topo
    """
    block_id = crc8(0, s, 0x31)%block

    s_d = crc8(0, s, 0x31)%2

    n1 = 128
    
    if block_id == 0:
        n2 = 128*3
        s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
        s_out, d_out = tors[s_out], tors[128 + d_out]
    elif block_id == 3:
        n2 = 128*3
        s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
        s_out, d_out = tors[128*block_id + s_out], tors[d_out]
    elif block_id == 1:
        out_block = random.randint(0, 2)
        if out_block == 0:
            n2 = 128
            s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
            s_out, d_out = tors[128*block_id + s_out], tors[d_out]
        elif out_block == 1:
            n2 = 128
            s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
            s_out, d_out = tors[128*block_id + s_out], tors[128*(block_id+1) + d_out]
        else:
            n2 = 128
            s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
            s_out, d_out = tors[128*block_id + s_out], tors[128*(block_id+2) + d_out]
    elif block_id == 2:
        out_block = random.randint(0, 2)
        if out_block == 0:
            n2 = 128
            s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
            s_out, d_out = tors[128*block_id + s_out], tors[d_out]
        elif out_block == 1:
            n2 = 128
            s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
            s_out, d_out = tors[128*block_id + s_out], tors[128*(1+1) + d_out]
        else:
            n2 = 128
            s_out, d_out = random.randint(0, n1-1), random.randint(0, n2-1)
            s_out, d_out = tors[128*block_id + s_out], tors[128*(block_id+1) + d_out]
            
        
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
    
def send_packet(hash_str, size, s, d, count_dict, count_dict1, mark_dict, 
        threshold, mark_group, seeds, polys, 
        flow_paths, cflow_dict, app_link_dict, app_link_flow_dict, switch_nodes, table, select_dict, drop_id=0, r_threshold=0.0, black_hole='sh41', test_hop='',
        add_byte_dict={}):
                
    """switch_id = mf.marknum(
            hash_str, count_dict, count_dict1, threshold, 
            mark_group[d]
    )"""
    pkt_mark = "0"
    if len(select_dict) < 1000000:
        pkt_mark = mf.mark_random(p=1.0)
    hash_str += pkt_mark
    if hash_str not in mark_dict:
        mark_dict[hash_str] = 0
    mark_dict[hash_str] += 1
    next_hop_rand_mark(
        s, 'h1', s, d, hash_str, size, table, seeds, polys, 
        flow_paths, cflow_dict, app_link_dict, app_link_flow_dict, select_dict,
        drop_id=drop_id, r_threshold=r_threshold, black_hole=black_hole, 
        test_hop=test_hop, add_byte_dict=add_byte_dict
    )
    
def flow_routing(file_name, seeds, polys, flow_paths,
                switch_nodes, table, flow_cap=1000, 
                topo_type='B4', task_type='CLASSIFICATION', 
                key='', class_dict={}, imr_threshold=0.1,
                k=3,
                drop_id=0, r_threshold=0.0, black_hole='sh41', links=[], 
                test_hop=''):
    mark_group = []
    #mark_group = mf.mark_group_dest(table)

    count = 0;
    start_time = 0;
    start_time0 = 0;
    is_update = True
    flow_dict = {}
    count_dict, threshold = {}, 100000
    mark_dict = {}
    count_dict1 = {}
    select_dict = {}
    cflow_dict = {}
    app_link_dict = {}
    app_link_flow_dict = {}
    perlink_df = pd.DataFrame()
    add_byte_dict={}
    
    with open((file_name), 'r') as f:
        for line in f:
            
            if(len(flow_dict) < 1824763):
                data = line.split()
              
                # Update start time
                if(is_update):
                    start_time = float(data[0])
                    start_time0 = float(data[0])
                    is_update = False
                
                if task_type != 'APPLICATION':
                    if len(select_dict) >= flow_cap: #20000:
                        break
                    
                if (float(data[0]) - start_time0) > 150:
                    is_update = True
                    print('Greater than 5.')
                    break
                    
                # Dominant applications and hash bias detection
                if task_type == 'APPLICATION':
                    if (float(data[0]) - start_time) > 1.0:
                    #if len(select_dict) >= flow_cap:
                        is_update = True
                        ap.appLinkCorrelation(
                            data, perlink_df, app_link_dict, cflow_dict, 
                            key=key, class_dict=class_dict, imr_threshold=imr_threshold,
                            k=k, 
                            topo_type=topo_type, links=links
                        )
                        break
                        
                if topo_type == 'JUPITER': #'JUPITER':
                    s, d = map_addr_tree_3(
                            data[2], data[3], switch_nodes
                            
                    ) #switch_nodes[:len(switch_nodes)/2],
                            #switch_nodes[len(switch_nodes)/2:]
                    if task_type == 'APPLICATION':
                        idx = int(data[7])
                        s, d = map_addr_tree_app(
                            data[2], data[3], switch_nodes[idx*128:(idx+1)*128]
                            
                    )

                else:
                    s, d = map_addr_tree(
                            data[2], data[3], 
                            switch_nodes
                    ) 
                #d = 'e1'
                hash_str = hashStr(data)  
                flow_dict[hash_str] = 1
                data_size = float(data[1])
                
                while(data_size > 0):
                    count += 1
                    per_size = data_size
                    send_packet(
                        hash_str, min(data_size, per_size), s, d, 
                        count_dict, count_dict1, 
                        mark_dict, threshold, mark_group, seeds, polys, 
                        flow_paths, cflow_dict, app_link_dict, app_link_flow_dict, switch_nodes, table, 
                        select_dict, drop_id=drop_id, r_threshold=r_threshold,
                        black_hole=black_hole, test_hop=test_hop, add_byte_dict=add_byte_dict
                    )
                    data_size -= per_size
                
            else:
                print(
                    '    -- time', (float(data[0]) - start_time0), 
                    'pkt count:', count, 'Flow num:', len(flow_dict)
                )
                break                
    return len(select_dict)

def write_list_file(data):
    """ Write to file
    """
    
    with open(("../outputs/tmp"), 'a') as f:
        for row in data:
            f.write(str(row) + '\n')

def subFlows(flow_paths, test_node):
    sub_flows = []
    for flow in flow_paths:
        if test_node in [y for x in flow[0].keys() for y in x]:
            sub_flows.append(flow)
    return sub_flows

def classification(cherns, chern_byte, d_min, p, s, sub_flows,
                    table, trues, ests, true_byte_dict, est_byte_dict,
                    pairs, epsilon=0.001):
    
    cherns[s], chern_byte[s], ds, d_min[s], p[s], true_class = mdt.hash_biased(
                s, sub_flows, table[s]
        )
    if s in [r1, r2]:    
        key = '-'.join(sorted([r1, r2]))
        if key not in true_byte_dict: 
            true_byte_dict[key] = [cherns[s], chern_byte[s], -1]
        true_byte_dict[key][0] = min(true_byte_dict[key][0], cherns[s])
        true_byte_dict[key][1] = min(true_byte_dict[key][1], chern_byte[s])
        
    if cherns[s] < epsilon:
        if s not in [r1, r2]:
            print(
                '        ++ s not in [r1, r2], d_min', 
                s, [r1, r2], d_min[s]
            )
            eeee
        key = ''.join(sorted([r1, r2]))
        if key not in trues: 
            trues[key] = cherns[s]
        trues[key] = min(trues[key], cherns[s])
        pairs.append([r1, r2, cherns[s], d_min[s], p[s]])
    return true_class

def classification_alg(true_byte_dict, epsilon=0.01, epsilon_pb=0.1):
    
    for key in true_byte_dict:
        if true_byte_dict[key][0] < epsilon:
            true_byte_dict[key][2] = 1
        if (true_byte_dict[key][0] >= epsilon
            and true_byte_dict[key][1] < epsilon_pb
        ):
            true_byte_dict[key][2] = 0
            
def single(r1, r2, pairs, est_pairs, switch_nodes, 
            trues, ests, true_byte_dict, est_byte_dict, table, test_nodes, 
            flow_cap=1000, is_correlated=True, topo_type='B4',
            task_type="CLASSIFICATION", 
            key='', class_dict={}, imr_threshold=0.1,
            epsilon=0.001,
            drop_id=0, r_threshold=0.0, black_hole='sh41', links=[]):
    
    print '**** correlation pair', r1, r2 
    true_class = -1
    if is_correlated:
        poly = set_correlation(r1, r2, polys)
        true_class = 1
    
    # Get the paths with at least two packets
    """
    flow_paths = ([(f[0].keys(), f[1]) 
            for f in flow_paths 
            for key in f[0] if f[0][key] > 1])
    print(flow_paths)
    eeeee
    """

    cherns, chern_byte = {}, {}
    d_min = {}
    p = {}
    
    if task_type != 'APPLICATION':
        for s in test_nodes:
            print '    **** testing node', s
            flow_paths = {}
            select_len = flow_routing(
                file_name, seeds, polys, flow_paths, switch_nodes, table, flow_cap,
                topo_type, 
                key=key, class_dict=class_dict, imr_threshold=imr_threshold,
                task_type=task_type, 
                drop_id=drop_id, r_threshold=r_threshold, black_hole=black_hole,
                links=links, test_hop=s
            )
            #print [flow_paths[key].values() for key in flow_paths.keys()[0:1]]
            flow_paths = ([(flow_paths[key], key[1], flow_paths[key].values()[-1]) 
                            for key in flow_paths]
            )
            print '**** Len(flow_paths)', len(flow_paths)
            #print flow_paths[0]
            
            sub_flows = subFlows(flow_paths, s)
            if task_type == "CLASSIFICATION":
                byte_true_class = classification(cherns, chern_byte, d_min, p, s, sub_flows,
                            table, trues, ests, true_byte_dict, est_byte_dict,
                            pairs, epsilon)
                if true_class == -1:
                    true_class = byte_true_class
            # Correlation ranking
            if task_type == "RANKING":
                ranking = locate_corr(s, sub_flows, table, epsilon)
                print '    -- ranking', ranking
                if len(ranking) != 0:
                    if (ranking[0][0] == r1 or ranking[0][0] == r2
                            or  (topo_type == 'JUPITER' 
                                and(('al' in s and 'ah' in ranking[0][0])
                                    or ('ah' in s and 'al' in ranking[0][0])
                                )
                            )
                    ):
                        key = '-'.join(sorted([r1, r2]))
                        if key not in ests:
                            ests[key] = ranking
                        if ranking[0][1] < ests[key][0][1]:
                            ests[key] = ranking
                        est_pairs.append((r1, r2))
                        
    if is_correlated:        
        reset_correlation(r2, polys, poly)
    
    return trues, ests, select_len, est_pairs, true_class

def locate_corr(s, flow_paths, table, threshould=0.01):

    cherns = mdt.corr_group(s, flow_paths, table, threshould)
    return cherns

def testPairs(G, aggr_nodes, prefix1='2_0', prefix2='2_1', table=None):
    """
    Return the pairs that may be correlated with each other
    """
    aggr1 = [x for x in aggr_nodes[1:80:8] if prefix1 in x]
    aggr2 = [x for x in aggr_nodes[0:80:8] if prefix2 in x]

    n = len(aggr1)
    
    test_pairs = []
    for i in range(0, n):
        for j in range(0, n):
            if (aggr1[i] in table and aggr2[j] in table 
                        and (aggr1[i], aggr2[j]) in G.edges()
                ):
                test_pairs.append((aggr1[i], aggr2[j]))
    
    return test_pairs

def jupiteNetwork():
    """
    Load jupiter network and build a graph
    """   
     
    # Build a graph for large clos topo
    tor_cut, aggr_cut, spine_cut = 512, 256, 256
    #2048, 4096, 4096 #32*4*2, 64*2, 16*2
    switches, edges = tp.jupiter_topo(
            tor_cut=tor_cut, aggr_cut=aggr_cut, spine_cut=spine_cut
    )
    
    G = build_graph(edges)
    external_edges = []
    for node in G.nodes():
        if 'sh' in node:
            G.add_edge(node, 'e1')
    
    """
    paths = list(nx.all_shortest_paths(G, 'tor385', 'tor1'))
    #print(paths)
    #eee
    paths = list(nx.all_shortest_paths(G, 'tor129', 'tor257'))
    #print(paths)
    paths = list(nx.all_shortest_paths(G, 'tor257', 'tor385'))
    #print(paths)
    #eee
    """
    switch_nodes, hnodes, tors, anodes, snodes = tp.getJupiternNodes(
            tors_num=tor_cut, aggr_num=aggr_cut, spine_num=spine_cut
    )
    print('**** is_connected(G)', nx.is_connected(G))
    print('**** number of components', nx.number_connected_components(G))
    
    tors = tors[0:512] + ['e1']

    # Get the routing path of all nodes
    table_file_name = '../outputs/jupiter_routing_table_anodes_cut4.txt'

    if((os.path.isfile(table_file_name)) == False):
        table = all_routing(G, tors, table_file_name)
    else:
        json_data = open(table_file_name).read()
        table = json.loads(json_data)
    
    seeds, polys = cf.get_seeds_table_jupiter(switch_nodes) #
    
    return G, tors, edges, table, seeds, polys, anodes
    
def smallClosNetwork():
    """
    Load small clos network and build a graph based on it
    """
    
    # Build a graph for Jupiter topo
    switch_nodes, edges = tp.tree_topo()
    G = build_graph(edges)
    nodes, host_nodes, tors, anodes, snodes = tp.getnodes()

    print('**** is_connected(G)', nx.is_connected(G))
    
    
    # Get the routing path of all nodes
    table_file_name = '../outputs/tree_routing_table.txt'
    if((os.path.isfile(table_file_name)) == False):
        table = all_routing(G, tors+['e1'], table_file_name)
    else:
        json_data = open(table_file_name).read()
        table = json.loads(json_data)
    
    print('**** Got routing table!')

    seeds, polys = cf.get_seeds_table_tree(switch_nodes) #
    
    return G, tors, edges, table, seeds, polys
    
def b4Wan():
    """
    Load a B4 Wan network and build a graph based on it
    """
    
    tors, edges = tp.mesh_topo()
    G = build_graph(edges)
    
    # Get the routing path of all nodes
    table_file_name = '../outputs/mesh_routing_table.txt'
    table = all_routing(G, tors, table_file_name)
    if((os.path.isfile(table_file_name)) == False):
        table = all_routing(G, tors, table_file_name)
    else:
        json_data = open(table_file_name).read()
        table = json.loads(json_data)
    
    seeds, polys = cf.get_seeds_table(tors) #

    return G, tors, edges, table, seeds, polys
    
if __name__ == "__main__":
    
    # Inputs as argv
    # Topo type: B4, TREE, JUPITER
    if len(sys.argv) >= 2:
        topo_type = sys.argv[1]
    else:
        topo_type = 'B4'
        
    # Variables
    if len(sys.argv) >= 3:
        flow_cap = int(sys.argv[2])
    else:
        flow_cap = 1000
    
    # Correlation or not: 1 and 0
    if len(sys.argv) >= 4:
        is_correlated = bool(int(sys.argv[3]))
    else:
        is_correlated = True
    
    # trace_type: A, B, C...
    if len(sys.argv) >= 5:
        trace_type = (sys.argv[4])
    else:
        trace_type = ''
    
    # Task type: CLASSIFICATION, RANKING, APPLICATION
    if len(sys.argv) >= 6:
        task_type = (sys.argv[5])
    else:
        task_type = 'CLASSIFICATION'
    
    # X variable tyepe
    if len(sys.argv) >= 7:
        x_var = (sys.argv[6])
    else:
        x_var = 'FLOWNUM'
        
    # P-value threshold
    if len(sys.argv) >= 8:
        epsilon = float(sys.argv[7])
    else:
        epsilon = 0.01
    
    # r_threshold
    if len(sys.argv) >= 9:
        r_threshold = float(sys.argv[8])
    else:
        r_threshold = 0.0
    
    # drop_id
    if len(sys.argv) >= 10:
        drop_id = int(sys.argv[9])
    else:
        drop_id = 0
    
    if len(sys.argv) >= 11:
        imr_threshold = float(sys.argv[10])
    else:
        imr_threshold = 0.1
        
    # Get network topo
    if topo_type == 'JUPITER':
        G, tors, edges, table, seeds, polys, anodes = jupiteNetwork()
    if topo_type == 'B4':
        G, tors, edges, table, seeds, polys = b4Wan()
    if topo_type == 'TREE':
        G, tors, edges, table, seeds, polys = smallClosNetwork()

    if trace_type == 'A':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_600s_clusterA_asort')
    elif trace_type == 'B':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_150s_web_sort_host')
    elif trace_type == 'C':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_600s_clusterC_asort')
    elif trace_type == 'e1':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_10s_web_sort_host_elephant_1flows')
    elif trace_type == 'e5':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_10s_web_sort_host_elephant_5flows')
    elif trace_type == 'e10':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_10s_web_sort_host_elephant_10flows')
    elif trace_type == 'e50':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_10s_web_sort_host_elephant_50flows')
    elif trace_type == 'e100':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_10s_web_sort_host_elephant_100flows')
    elif trace_type == 'ABC':
        file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                    + 'split_flows_10s_clusterABC_asort')
                    
    if topo_type == 'B4':
        test_pairs = ([('s3', 's4'), ('s4', 's3'),  
                    ('s3', 's6'), ('s6', 's3'), 
                    ('s4', 's5'), ('s5', 's4'),
                    ('s5', 's6'), ('s6', 's5')]
        ) 

        if task_type == 'APPLICATION':
            test_pairs = [('s4', 's3')]
    if topo_type == 'TREE':
        test_pairs = ([('2_0_0_0', '2_1_0_0'), ('2_0_0_1', '2_1_0_1'), 
                        ('2_0_0_2', '2_1_0_2'), ('2_0_0_3', '2_1_0_3'),
                        ('2_0_1_0', '2_1_1_0'), ('2_0_1_1', '2_1_1_1'), 
                        ('2_0_1_2', '2_1_1_2'), ('2_0_1_3', '2_1_1_3')])
        if task_type == 'APPLICATION':
            test_pairs = [('2_0_0_0', '2_1_0_0')]
        #test_pairs = [('2_0_0_0', '2_1_0_0'), ('2_0_0_0', '3_0_0_0')]
    """test_pairs = testPairs(
            G, anodes[0:80], prefix1='ah', prefix2='al', table=table
    )""" 
    
    if topo_type == 'JUPITER':
        test_pairs = []
        for i in range(1, 1+32*8, 32): # 1, 65, 129, 193
            if i != 129:
                test_pairs.append(('al'+str(i), 'ah'+str(i)))
                test_pairs.append(('al'+str(i), 'ah'+str(i+1)))
                #test_pairs.append(('ah'+str(i), 'sl'+str(i)))
        #test_pairs = [('al1', 'sl81')]
                
        if task_type == 'APPLICATION':
            links = list(nx.all_shortest_paths(G, 'tor1', 'e1'))
            test_pairs = sorted(
                list(set([(x[2], x[3]) for x in links])), key=lambda x:x[0])[0:16]          
    
    pairs, est_pairs = [], []
    trues, ests = {}, {}
    true_byte_dict, est_byte_dict, true_class_dict = {}, {}, {}
    class_dict = {}
    for (r1, r2) in test_pairs:
        if task_type == 'APPLICATION':
            black_hole = [x for x in G[r2] if 'sh' in x][0]
        #elif task_type == 'CLASSIFICATION'
            #black_hole = [x for x in G[r2] if 'sh' in x][0]
        else:
            black_hole = None
        links = sorted(
            [(r2, x) for x in G[r2] if 'sh' in x], key=lambda x: x[1])

        if r1 != r2:
            key = '-'.join(sorted([r1, r2]))
            trues, ests, select_len, est_pairs, true_class_dict[key] = single(
                r1, r2, pairs, est_pairs, tors, 
                trues, ests, true_byte_dict, est_byte_dict, 
                table, [r1, r2],
                flow_cap,
                is_correlated,
                topo_type,
                task_type=task_type,
                key=key, class_dict=class_dict, imr_threshold=imr_threshold,
                epsilon=0.01,
                drop_id=drop_id, r_threshold=r_threshold,
                black_hole=black_hole,
                links=links
            )
                
    print(
        'trues, ests, select_len, est_pairs', 
        len(trues), len(ests), select_len, est_pairs
    )
    classification_alg(true_byte_dict, epsilon=0.01, epsilon_pb=epsilon)
    
    # Write to fsile
    file_name1, file_name2 = cf.init_files(trace_type=trace_type, 
                task_type=task_type, topo_type=topo_type, 
                x_var=x_var, p=0.01)
            
    f1 = open(file_name1, 'a')
    f2 = open(file_name2, 'a')
    if task_type == "CLASSIFICATION":
        for key in true_byte_dict:
            true_class = is_correlated
            if r_threshold <= 0:
                true_class  = -1
                is_correlated = -1
            f2.write(
                    str(select_len) + ','
                    + str(epsilon) + ','
                    + str(int(is_correlated)) + ','
                    + key + ','
                    + str(true_byte_dict[key][0]) + ',' 
                    + str(true_byte_dict[key][1]) + ','
                    + str(true_byte_dict[key][2]) + ','
                    + str(int(true_class)) + '\n' #true_class_dict[key]
            )
        
        f1.write(
            ','.join([str(x) for x in 
            [select_len, epsilon, int(is_correlated), len([x for x in true_byte_dict.values() if x[2] == 1]), 
            len([x for x in true_byte_dict.values() if x[2] == 0]), 
            len(true_byte_dict)]]
            ) 
            + '\n'
        )
    
    if task_type == "RANKING":    
        # Ranking result
        for key in ests:
            f2.write(
                    str(select_len) + ','
                    + str(epsilon) + ','
                    + str(int(is_correlated)) + ','
                    + key + ','
                    + str(len(ests)) + ','
                    + str([(x[2]) for x in ests[key]][0]) + ','
                    + ','.join([str(x[1]) for x in ests[key]]) + ','
                    + ','.join([str(x[0]) for x in ests[key]]) + '\n'
            )
 
        f1.write(
            ','.join([str(x) for x in 
            [select_len, epsilon, int(is_correlated), 
            len(ests)]]
            ) 
            + '\n'
        )
    
    if task_type == "APPLICATION":    
        # Ranking result
        true_num = 0
        for key in class_dict:
            true_class = 0
            true_class = 1 if is_correlated else 2 if r_threshold>0 else 0
            f2.write(
                    str(select_len) + ','
                    + str(r_threshold) + ','
                    + str(imr_threshold) + ','
                    + str(int(is_correlated)) + ','
                    + str(int(drop_id)) + ','
                    + key + ','
                    + str(class_dict[key]) + ','
                    + str(true_class) + '\n'
            )
            if true_class == class_dict[key]:
                true_num += 1
 
        f1.write(
            ','.join([str(x) for x in 
            [select_len, r_threshold, imr_threshold, int(is_correlated), 
            true_num, len(class_dict)]]
            ) 
            + '\n'
        )
    
