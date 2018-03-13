from collections import OrderedDict
import bound as bd
import numpy as np
from crc32 import crc32
import random

def collect_flows(hash_str, pre_hop, cur_hop, 
            size, cflow_dict, 
            app_link_dict, app_link_flow_dict, next_hops='', d='tor1'
    ):
    # hash_str: 4+4+2+2
    # Per link. Per app,     
    if (pre_hop, cur_hop) not in cflow_dict:
        cflow_dict[(pre_hop, cur_hop)] = {}
    dst_port = hash_str[10:12]
    dst_tor = int(int(d[3:])/129)
    key = dst_tor
    if key not in cflow_dict[(pre_hop, cur_hop)]:
        cflow_dict[(pre_hop, cur_hop)][key] = 0
    cflow_dict[(pre_hop, cur_hop)][key] += size
    
    # Per link, Per app, flow count
    if (pre_hop, cur_hop) not in app_link_dict:
        app_link_dict[(pre_hop, cur_hop)] = {}
        app_link_flow_dict[(pre_hop, cur_hop)] = {}
        
    dst_port = hash_str[10:12]
    dst_tor = int(int(d[3:])/129)
    key = dst_tor
    if key not in app_link_dict[(pre_hop, cur_hop)]:
        app_link_dict[(pre_hop, cur_hop)][key] = 0
        app_link_flow_dict[(pre_hop, cur_hop)][key] = {}
    if hash_str not in app_link_flow_dict[(pre_hop, cur_hop)][key]:
        app_link_flow_dict[(pre_hop, cur_hop)][key][hash_str] = 0
        app_link_dict[(pre_hop, cur_hop)][key] += 1
        
def append_path(hash_str, pre_hop, cur_hop, d, paths, size=1):
    if (hash_str, d) not in paths:
        paths[(hash_str, d)] = OrderedDict({})
    if (pre_hop, cur_hop) not in paths[(hash_str, d)]:
        paths[(hash_str, d)][(pre_hop, cur_hop)] = 0
    paths[(hash_str, d)][(pre_hop, cur_hop)] += size #int(max(1, size/500))
    
def min_bound(next_counts, flow_indicator=1):
    
    n = len(next_counts)
    min_bound = 1.1
    min_pos = -1
    if flow_indicator == 1:
        sum_HHes = np.float64(((sum(next_counts))))
    else:
        sum_HHes = np.float64(sum([x for sub in next_counts for x in sub]))
        
    for i in range(n):
        if flow_indicator == 1:
            o_fi = float((next_counts[i]))/sum_HHes
        else:
            o_fi = float(sum(next_counts[i]))/sum_HHes
            """print(
                '        %%next_bytes, o_fi', 
                [sum(sub) for sub in next_counts], 
                o_fi
            )"""
        ratio = 1.0/len(next_counts)
        """print(
                '        %%next_counts, o_fi, ratio', next_counts, o_fi, ratio
        )"""
        if o_fi <= ratio:
            if flow_indicator == 1:
                flow_fractions = [float(1.0)/sum_HHes]*sum_HHes
            else:
                flow_fractions = ([x/sum_HHes for sub in next_counts 
                                                for x in sub]
                )
                
            theta, chern_bound = bd.chernoff_min(
                    flow_fractions, o_fi, ratio=ratio
            )
            if chern_bound < min_bound:
                min_bound = chern_bound
                min_pos = i
    # print('        %%min_bound', min_bound)
    return min_bound

class singleNode(object):
    def __init__(self, val):
        self.val = val
        self.pre = None
        self.next = None
        
def makelist(points):
    d = {}
    p = None
    
    count = 0
    while(count < 2):
        count += 1
        for point in points:
            if point[0] not in d:
                snode0 = singleNode(point[0])
                d[point[0]] = snode0
            else:
                snode0 = d[point[0]]
                
            if point[1] not in d:
                snode1 = singleNode(point[1])
                d[point[1]] = snode1
            else:
                snode1 = d[point[1]]
            
            snode0.next = snode1
            snode1.pre = snode0
        
    p = snode0
    while(p.pre != None):
        p = p.pre
    
    nodes = []
    while(p != None):
        nodes.append(p.val)
        p = p.next
    return nodes

def get_seeds_table(router_nodes):
    """
    Assign seed and polinmial to node.
    """
    poly_list = (
            [0x31, 0x2f, 0x39, 0xd5, 0x4d, 
            0x8d, 0x9b, 0x7a, 0x07, 0x49, 
            0x1d, 0x2d, 0x3d, 0x8b, 0x7b]
    )
    
    np = len(poly_list)   
    seeds = {}
    polys = {}
    i = 0
    
    for node in router_nodes:
        seeds[node] = crc32(node)%256
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

def get_seeds_table_tree(router_nodes):
    """
    Assign seed and polinmial to node.
    """
    poly_list = (
            [0x31, 0x2f, 0x39, 0xd5, 0x4d, 0x8d, 
            0x9b, 0x7a, 0x07, 0x49, 0x1d, 0x2d, 
            0x3d, 0x8b, 0x7b, 0xff, 0xef, 0xdf, 
            0xcf, 0xbf, 0xaf, 0x9f, 0x8f, 0x7f,
            0x6f, 0x5f, 0x4f, 0x3f, 0x1f, 0xde, 
            0xce, 0xbe, 0xae, 0x9e, 0x8e, 0x7e,
            0x6e, 0x5e, 0x4e, 0x3e, 0x2e]
    )
    
    np = len(poly_list)   
    seeds = {}
    polys = {}
    i = 0
    
    for node in router_nodes:
        seeds[node] = crc32(node)%256

        if i < np:
            polys[node] = poly_list[i]
        else:
            k = random.randint(0, np-1)
            polys[node] = poly_list[k]
        i += 1
    
    return seeds, polys

def get_seeds_table_jupiter(router_nodes):
    """
    Assign seed and polinmial to node.
    """
    
    poly_list = (
            [0x31, 0x2f, 0x39, 0xd5, 0x4d, 0x8d, 
            0x9b, 0x7a, 0x07, 0x49, 0x1d, 0x2d, 
            0x3d, 0x8b, 0x7b, 0xff, 0xef, 0xdf, 
            0xcf, 0xbf, 0xaf, 0x9f, 0x8f, 0x7f,
            0x6f, 0x5f, 0x4f, 0x3f, 0x1f, 0xde, 
            0xce, 0xbe, 0xae, 0x9e, 0x8e, 0x7e,
            0x6e, 0x5e, 0x4e, 0x3e, 0x2e]
    )
    
    np = len(poly_list)   
    seeds = {}
    polys = {}
    i = 0
    d = {'tor': 0x31, 'al': 0x2f, 'ah': 0x39, 'sl': 0xd5, 'sh': 0x4d}
    for node in router_nodes:
        seeds[node] = crc32(node)%256

        for key in d:
            if key in node:
                polys[node] = d[key]
            i += 1
    
    return seeds, polys

def init_files(trace_type = ' ', task_type='CLASSIFICATION', topo_type='b4', 
                x_var = 'FLOWNUM', p=0.01
    ):
    file_name1 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_trace'+trace_type+'_p'+str(p)+'.csv')
    file_name2 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_chern_trace'+trace_type+'_p'+str(p)+'.csv')
            
    return file_name1, file_name2   
    
