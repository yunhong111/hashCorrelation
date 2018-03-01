import numpy as np
import bound as bd
import co_func as cf
from co_func import min_bound
from t_test import t_test, t_test_byte

def common_flows_with_next(r2, r2_next_hops, 
                            d, flow_paths, routing_table
        ):
    
    next_counts = {}
    next_bytes = {}
    for nhop in r2_next_hops:
        next_counts[nhop] = 0
        next_bytes[nhop] = []
    x = {}    
    for f_path in flow_paths:
        dst = f_path[1]
        if dst in d:
            for edge in f_path[0]:
                if edge[0] == r2:
                    if edge[1] in r2_next_hops:
                        next_counts[edge[1]] += 1
                        next_bytes[edge[1]].append(f_path[2])
                        if (dst, edge[1]) not in x:
                            x[(dst, edge[1])] = 0
                        x[(dst, edge[1])] += 1
    
    return next_counts.values(), next_bytes.values(), x

def getIndex(qlist, value):
    idx = -1
    try:
        idx = qlist.index(value, idx + 1)
    except ValueError:
        return idx
    return idx
    
def common_flows_with_pre(prehop, r2, r2_next_hops, 
                            d, d_pre, flow_paths, 
                            routing_table
        ):
            
    next_counts = {}
    next_bytes = {}
    for nhop in r2_next_hops:
        next_counts[nhop] = 0
        next_bytes[nhop] = []

    # r2 is the previous hop of next hops
    for f_path in flow_paths:

        dst = f_path[1]
        ps = cf.makelist(f_path[0])
        idx_pre = getIndex(ps, prehop)
        idx_cur = getIndex(ps, r2)
            
        if (idx_pre >= 0 and idx_cur >= 0 
                    and idx_cur > idx_pre 
                    and dst in d and dst in d_pre
            ):
            
            for nhop in r2_next_hops:
                if (r2, nhop) in f_path[0]:
                    next_counts[nhop] += 1
                    next_bytes[nhop].append(f_path[2])
                    break
                
    #print('        ^^ common_flows_with_pre:next_counts', next_counts)           
    return next_counts.values(), next_bytes.values()
    
def dest_group_by_nhops(routing_table):
    # ds with the same next hops
    # [[d1, d2], [], [], []]
    # key is the next hops, value is the dest
    
    ds = {}
    dests = routing_table.keys()
    
    d_n = len(dests)
    visited = [False for i in range(d_n)]
    for i, d in enumerate(dests):
        if len(routing_table[d]) > 1 and visited[i] == False:
            nhops = sorted(routing_table[d])
            tmp = [d]
            for j in range(i+1, d_n):
                d_j = dests[j]
                if sorted(routing_table[d_j]) == nhops:
                    visited[j] = True
                    tmp.append(d_j)
            ds['\t'.join(nhops)] = tmp
    return ds
    
def hash_biased(r1, flow_paths, routing_table_r1, 
                threshould=0.0001
        ):
    """
    routing_table is the table of r1
    """
    ds = dest_group_by_nhops(routing_table_r1)
    min_chern = 2.0
    min_chern_byte = 2.0
    d_min = None
    p_min, p_byte_min = 2.0, 2.0
    true_class = -1
    if len(ds) != 0:
        for key in ds.keys():
            nhops = key.split('\t')
            next_counts, next_bytes, x = common_flows_with_next(
                    r1, nhops, ds[key], flow_paths, 
                    routing_table_r1
            )
                
            chern_bound = 0
            if max(next_counts) > 5:
                chern_bound = min_bound(next_counts)
                if min_chern > chern_bound:
                    d_min = (key, ds[key], x)
                min_chern = min(min_chern, chern_bound)
                cut = max(1, int(1*min(map(len, next_bytes))))
                next_bytes_sorted = [(x[-cut:]) for x in map(sorted, next_bytes)]
                sum_next_bytes = map(sum, next_bytes_sorted)
                
                chern_byte = min_bound(next_bytes, flow_indicator=0)
                min_chern_byte = min(min_chern_byte, chern_byte)
                
                t, p = t_test(next_counts, 0.5)
                t_byte, p_byte = t_test_byte(next_bytes, 0.5)
                p_byte_min = min(p_byte_min, p_byte)
                
                if ((max(sum_next_bytes) - min(sum_next_bytes))/max(sum_next_bytes) > 0.8
                        and min(next_counts) > 5):
                #if p_byte < 0.1:
                    true_class = 0
                
                print 'true_class', cut, (max(sum_next_bytes) - min(sum_next_bytes))/max(sum_next_bytes), true_class, sum_next_bytes, next_counts, p_byte, chern_byte
                
                if p_min > p: # and max(next_counts) > 50:
                    p_min = p
                    d_min = (key, ds[key], x, next_counts)
                
                #if min_chern < threshould:
                    #break
                #print('        ^^nhops, next_counts', nhops, next_counts)
    
    return min_chern, min_chern_byte, [r1, ds], d_min, p_min, true_class

def corr_detection(r1_pre, r1, flow_paths, 
                    routing_table_pre, routing_table_r1
        ):
    
    d_pres = dest_group_by_nhops(routing_table_pre)
    d_pre_list = [x for d_pre in d_pres.values() for x in d_pre]
    ds = dest_group_by_nhops(routing_table_r1)
    min_chern = 2.0
    min_chern_byte = 2.0
    p_min = 2.0
    if len(ds) != 0:
        for key in ds.keys():
            nhops = key.split('\t')
            if len(set(d_pre_list).intersection(ds[key])) == 0:
                continue
            next_counts, next_bytes = common_flows_with_pre(
                    r1_pre, r1, nhops, 
                    d_pre_list, ds[key], flow_paths, 
                    routing_table_r1
            )
            if sum(next_counts) > 10:
                t, p = t_test(next_counts, 0.5)
            chern_bound = 0
            if sum(next_counts) > 10: # and max(next_counts) > 50:
                chern_bound = min_bound(next_counts)
                min_chern = min(min_chern, chern_bound)
                p_min = min(p_min, p)
                
                chern_byte = min_bound(next_bytes, flow_indicator=0)
                min_chern_byte = min(min_chern_byte, chern_byte)
                
    """print(
        '        ^^min_chern, p, min_chern_byte', 
                min_chern, p_min, min_chern_byte
    )"""
    
    return min_chern, p_min
    
def corr_group(r2, flow_paths, routing_table, threshould=0.01):
    """
        input:
        list[str]: n*1
        routing_matrix:  
        r1s, r2: ancesters of r2: r1 and router r2
    """
    
    r1s = pre_hop_group(r2, flow_paths, routing_table[r2])
    min_bounds = []
    for r1 in r1s:
        min_bound, p = corr_detection(
                r1, r2, flow_paths, routing_table[r1], routing_table[r2]
        )
        #if p != 0:
            #min_bound = min(min_bound, p)
        #if min_bound < threshould:
        min_bounds.append((r1, min_bound))
    
    min_bounds = sorted(min_bounds, key=lambda x: x[1])
    
    return min_bounds

def pre_hop_group(r1, flow_paths, routing_table_r1):
    
    ds = dest_group_by_nhops(routing_table_r1)
    all_pres = []

    if len(ds) != 0:
        for key in ds.keys():
            nhops = key.split('\t')
            pres = pre_hops(
                        r1, nhops, ds[key], flow_paths
            )
            all_pres.append(pres)
    all_pres = list(set([x for pre in all_pres for x in pre]))
    
    return all_pres
        
def pre_hops(r2, r2_next_hops, d, flow_paths):
    """
        The pre hops of r1 based on the splitting, 
        (2, 1) (4, 3) (5, 6) (3, 5) (1, 4) 
        (2, 1) (1, 4) (4, 3) (3, 5) (5, 6)
    """
    
    # r2 is the previous hop of next hops
    pres = []
    for f_path in flow_paths:
        dst = f_path[1]
        if dst in d:
            ps = cf.makelist(f_path[0])
            nodes = []
            if r2 in ps:
                for p in ps:
                    if r2 == p:
                        break
                    if 'h' not in p:
                        nodes.append(p)
                
                pres += nodes
            
    return list(set(pres))

def other_hops(r2, flow_paths):
    """
        Other hops in the path
    """
    
    # r2 is the previous hop of next hops
    out_nodes = []
    for f_path in flow_paths:
        nodes = list(set([x for y in f_path[0] for x in y if 'h' not in x]))
        print('f_path', f_path)
        if r2 in nodes:
            nodes.remove(r2)
            for node in nodes:
                if (r2, node) in f_path[0]:
                    nodes.remove(node)
                    out_nodes += nodes
    #print('        ^^ other_hops:nodes', list(set(out_nodes)))
    return list(set(out_nodes))
    
