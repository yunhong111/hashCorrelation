import numpy as np
import bound as bd
from co_func import min_bound

def common_flows_with_next(r2, r2_next_hops, 
                            d, flow_paths, router_nodes, routing_table
        ):
    
    next_counts = {}
    for nhop in r2_next_hops:
        next_counts[nhop] = 0
        
    for f_path in flow_paths:
        for edge in f_path:
            if edge[0] == r2:
                for nhop in r2_next_hops:
                    if edge[1] == nhop:
                        next_counts[nhop] += 1
    
    print('r2, next_counts', r2, next_counts)
    return next_counts.values()

def common_flows_with_pre(prehop, r2, r2_next_hops, 
                            d, d_pre, flow_paths, 
                            router_nodes, routing_table
        ):
            
    next_counts = {}
    for nhop in r2_next_hops:
        next_counts[nhop] = 0
        
    # r2 is the previous hop of next hops
    for f_path in flow_paths:
        is_pre_onpath = False
        is_cur_onpath = False
        cur_edge = None
        for edge in f_path:
            if edge[0] == prehop:
                is_pre_onpath = True
            if edge[0] == r2:
                is_cur_onpath = True
                cur_edge = edge
        if is_pre_onpath and is_cur_onpath:
            if cur_edge[1] == nhop:
                next_counts[nhop] += 1
                
    
    print('r2, next_counts', r2, next_counts)
    return next_counts.values()
    
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
    
def hash_biased(r1, flow_paths, router_nodes, routing_table_r1, 
                threshould=0.001
        ):
    """
    routing_table is the table of r1
    """
    ds = dest_group_by_nhops(routing_table_r1)
    print('ds', r1, ds)
    min_chern = 2.0
    if len(ds) != 0:
        for key in ds.keys():
            nhops = key.split('\t')
            next_counts = common_flows_with_next(
                    r1, nhops, ds[key], flow_paths, 
                    router_nodes, routing_table_r1
            )
            chern_bound = 0
            if sum(next_counts) > 0:
                chern_bound = min_bound(next_counts)
                min_chern = min(min_chern, chern_bound)
                if min_chern < threshould:
                    break
    return min_chern, [r1, ds]

def corr_detection(r1_pre, r1, flow_paths, router_nodes, 
                    routing_table_pre, routing_table_r1
        ):
    
    d_pres = dest_group_by_nhops(routing_table_pre)
    d_pre_list = [x for d_pre in d_pres.values() for x in d_pre]
    ds = dest_group_by_nhops(routing_table_r1)
    print('r1, ds, d_pre_list', r1, ds, d_pre_list)
    min_chern = 2.0
    if len(ds) != 0:
        for key in ds.keys():
            nhops = key.split('\t')
            next_counts = common_flows_with_pre(
                    r1_pre, r1, nhops, 
                    d_pre_list, ds[key], flow_paths, 
                    router_nodes, routing_table_r1
            )
            chern_bound = 0
            if sum(next_counts) > 0:
                chern_bound = min_bound(next_counts)
                min_chern = min(min_chern, chern_bound)
    return min_chern

def corr_group(r2, flow_paths, router_nodes, routing_table):
    # input:
    # list[str]: n*1
    # routing_matrix:  
    # r1s, r2: ancesters of r2: r1 and router r2
    r1s = pre_hop_group(r2, flow_paths, router_nodes, routing_table[r2])
    min_bounds = []
    for r1 in r1s:
        min_bound = corr_detection(
                r1, r2, flow_paths, router_nodes, 
                routing_table[r1], routing_table[r2]
        )
        min_bounds.append((r1, min_bound))
    min_bounds = sorted(min_bounds, key=lambda x: x[1])
    return min_bounds

def pre_hop_group(r1, flow_paths, router_nodes, routing_table_r1):
    
    ds = dest_group_by_nhops(routing_table_r1)
    all_pres = []

    if len(ds) != 0:
        for key in ds.keys():
            nhops = key.split('\t')
            pres = pre_hops(
                        r1, nhops, ds[key], flow_paths, 
                        router_nodes, routing_table_r1
            )
            print('pres', pres)
            all_pres.append(pres)
    all_pres = list(set([x for pre in all_pres for x in pre]))
    return all_pres
            
def pre_hops(r2, r2_next_hops, d, flow_paths, router_nodes, routing_table):
    """
    The pre hops of r1 based on the splitting, 
    """
    r2_pos = router_nodes.index(r2)
    rm_r2_nhops = []
    
    # r2 is the previous hop of next hops
    for f in rm:
        for npos in r2_next_hops:
            
            next_pos = router_nodes.index(npos)
            dst = router_nodes[f.index(max(f))]
            
            if (f[r2_pos] != 0 
                    and f[next_pos] != 0 
                    and f[r2_pos] < f[next_pos] 
                    and dst in d
                    ):
                rm_r2_nhops.append(f)
    rm = rm_r2_nhops
    if len(rm) == 0:
        print('++++ pre_hops, rm is empty, r2, r2_next_hops', r2, r2_next_hops)
        return []
    print('rm', rm)

    pres = {}
    for f in rm:
        for x in f:
            if x < f[r2_pos] and x != 0:
                pre = router_nodes[f.index(x)]
                pres[pre] = 1
    print('pres', r2, pres)
    return pres.keys()
    
