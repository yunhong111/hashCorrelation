import numpy as np
import bound as bd
from co_func import min_bound

def common_flows(r1, r2, rm, router_nodes, port_list):
    rm = np.array(rm, dtype=bool)
    rm = np.array(rm, dtype=int)
    r1_pos = router_nodes.index(r1)
    r2_pos = router_nodes.index(r2)
    r2_next_hops = port_list[r2].split()
    next_counts = []
    for r2_next_hop in r2_next_hops:
        next_pos = router_nodes.index(r2_next_hop)
        m_r1_r2 = np.bitwise_and(
                rm[:, r1_pos], rm[:, r2_pos])
        next_flows = np.bitwise_and(
                m_r1_r2, rm[:, next_pos])
        next_count = sum(next_flows)
        next_counts.append(next_count)
    print(r1, r2, next_counts)
    return next_counts  
    
def corr_detection(r1, r2, rm, router_nodes, port_list):
    # input:
    # list[str]: n*1
    # routing_matrix:  
    # r1, r2: two routers, r1 is the ancester of r2
    
    next_counts = common_flows(r1, r2, rm, router_nodes, port_list)
    return min_bound(next_counts)

def corr_group(r1s, r2, rm, router_nodes, port_list):
    # input:
    # list[str]: n*1
    # routing_matrix:  
    # r1s, r2: ancesters of r2: r1 and router r2
    
    min_bounds = []
    for r1 in r1s:
        min_bound = corr_detection(r1, r2, rm, router_nodes, port_list)
        min_bounds.append(min_bound)
    return min_bounds
    

    
    
            
        
    
