import binascii
import zlib
import netaddr
import socket, sys
import numpy as np
import crcmod
import pandas as pd
import os
import md5
import math
import random
import matplotlib.pyplot as plt
from itertools import chain
import bound  
from crc8 import crc8
from crc32 import crc32
import connection as con
import topo
import sketch as sk
from path_matrix import path_matrix
import detection as dt
   
def get_seeds_table():
    """
    Assign seed and polinmial to node.
    """
    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes = topo.getnodes()
    poly_list = (
            [0x31, 0x2f, 0x39, 0xd5, 0x4d, 0x8d, 0x9b, 0x7a, 0x07, 0x49, 0x1d]
    )
        
    seeds = {}
    polys = {}
    i = 0
    router_nodes = tor_nodes + aggr_nodes + spine_nodes
    
    for node in router_nodes:
        if(node != '3_1_0_0'
                and node != '3_1_0_1'and node != '3_1_1_0'
                and node != '3_1_1_1'):      
            seeds[node] = i*7
            layer = int(node[0]) + int(node[2]) - 1
            if(node[0] == '3'):
                layer = int(node[0]) + int(node[2])

            polys[node] = poly_list[layer]
            i += 1
            
    count = len(poly_list) - 1
    polys['2_0_0_0'] =  poly_list[count]
    count -= 1
    polys['2_1_0_0'] =  poly_list[count]
    count -= 1

    polys['3_0_0_0'] = polys['2_0_0_0']
    return seeds, polys

def routing(file_name, seeds, polys, port_list, link_loads, node_loads, paths):
    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes = topo.getnodes()
    
    count = 0;
    start_time = 0;
    is_update = True
    
    with open((file_name), 'r') as f:
        for line in f:
            count += 1
            if(count < 10000000):
                data = line.split()
              
                # Update start time
                if(is_update):
                    start_time = float((data[0]))
                    is_update = False
                  
                # Monitor every second
                if (float(data[0]) - start_time) > 1:
                    is_update = True
                    print('Greater than 1.')
                    break
                  
                hash_str = (data[2]
                        + '\t' + data[3]
                        + '\t' + data[4]
                        + '\t' + data[5]
                        + '\t' + data[6]
                )
                        
                ev = crc32(hash_str)
                size = int(float(data[1])) 
              
                port = int(data[7])
                next_hop = host_nodes[port]
                
                con.host_up(
                        next_hop, ev, hash_str, size, seeds, polys, port_list,
                        link_loads, node_loads, paths
                )
            else:
                break                  

def link_load_init(port_list):
    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes = topo.getnodes()
    link_byte_cnt = {}
    for node in nodes:
        next_hops = port_list[node].split()
        for next_hop in next_hops:
            link_byte_cnt[node + ' '+next_hop] = 0
    return link_byte_cnt            

def node_load_init():
    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes = topo.getnodes()
    byte_cnt = {}
    for node in nodes:
        byte_cnt[node] = 0    
    return byte_cnt
    
if __name__ == '__main__':    
    
    if(len(sys.argv) == 1):
        sys.argv.append('1')
    is_byte = bool(int(sys.argv[1]))

    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes = topo.getnodes()
    port_list = topo.get_nexthos_up()
    seeds, polys = get_seeds_table()
    link_loads = link_load_init(port_list)
    node_loads = node_load_init()
    
    file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                + "split_flows_1s_web_sort_host_alpha_1.25"
    )
            
    flow_packs = {}
    paths = {}
    routing(file_name, seeds, polys, port_list, node_loads, link_loads, paths)
    
    router_nodes = tor_nodes + aggr_nodes + spine_nodes
    rm = path_matrix(paths, router_nodes)
    
    r1s = ['2_0_0_0', '2_0_0_1', '2_0_1_0', '2_0_1_1', '2_1_0_0', '2_1_1_0']
    r1 = '2_0_0_0'
    r1 = '2_1_0_0'
    r2 = '3_0_0_0'
    
    min_bounds = dt.corr_group(r1s, r2, rm, router_nodes, port_list)
    print('min_bounds', min_bounds)
    print(node_loads)

