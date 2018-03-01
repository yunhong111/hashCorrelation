from crc8 import crc8 
from collections import OrderedDict
from co_func import append_path
          
def host(pre_hop, cur_hop, ev, hash_str, size, byte_cnt, link_byte_cnt, paths):
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    
def tor_sw(pre_hop, cur_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths):
    
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    
    # Generate random port
    port_num = 2
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
    
    next_hop = port_list[cur_hop].split()[port]
    host(cur_hop, next_hop, ev, hash_str, size, byte_cnt, link_byte_cnt, paths)
    
def aggr_sw(pre_hop, cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    
    # Generate random port
    port_num = 2
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
        
    next_hop = port_list[cur_hop].split()[port]
    tor_sw(
        cur_hop, next_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths
    )
        
def spine_sw(cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    byte_cnt[cur_hop] += size
    
    port_num = 4
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
    
    next_hop = port_list[cur_hop].split()[port]
    aggr_sw(
        cur_hop, next_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths
    )

def host_up(cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    
    #append_path(hash_str, cur_hop, paths)
    byte_cnt[cur_hop] += size
    next_hop = port_list[cur_hop]
    tor_sw_up(
        cur_hop, next_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths
    )

def tor_sw_up(pre_hop, cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    append_path(hash_str, cur_hop, paths)
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    port_num = 4
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
    next_hop = port_list[cur_hop].split()[port]
    aggr_sw_up_0(
        cur_hop, next_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths
    )

def aggr_sw_up_0(pre_hop, cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    append_path(hash_str, cur_hop, paths)
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    port_num = 2
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
    next_hop = port_list[cur_hop].split()[port]
    aggr_sw_up_1(
        cur_hop, next_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths
    )

def aggr_sw_up_1(pre_hop, cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    append_path(hash_str, cur_hop, paths)
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    port_num = 2
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
    next_hop = port_list[cur_hop].split()[port]
    spine_sw_up_0(
        cur_hop, next_hop, ev, hash_str, size, seeds, polys, port_list, 
        byte_cnt, link_byte_cnt, paths
    )

def spine_sw_up_0(pre_hop, cur_hop, ev, hash_str, size, seeds, polys, port_list, 
            byte_cnt, link_byte_cnt, paths):
    append_path(hash_str, cur_hop, paths)
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
    port_num = 2
    port = crc8(seeds[cur_hop], (hash_str), polys[cur_hop])%port_num
    next_hop = port_list[cur_hop].split()[port]
    spine_sw_up_1(
        cur_hop, next_hop, ev, hash_str, size, byte_cnt, link_byte_cnt, paths
    )

def spine_sw_up_1(pre_hop, cur_hop, ev, hash_str, size, 
        byte_cnt, link_byte_cnt, paths):
    append_path(hash_str, cur_hop, paths)
    byte_cnt[cur_hop] += size
    link_byte_cnt[pre_hop+' '+cur_hop] += size
