import pandas as pd
import os.path
import json

def getnodes():
    nodes = []    
    # Host name 
    host_nodes = []
    for i in xrange(0,8):
        for j in xrange(0,2):
            name = str(0)+'_'+str(0)+'_' + str(j)+'_' +str(i)
            nodes.append(name)
            host_nodes.append(name)
    
    # ToR name 
    tor_nodes = []
    for i in xrange(0,8):
        for j in xrange(0,2):
            name = str(1)+'_'+str(0)+'_' + str(j)+'_' +str(i)
            nodes.append(name)
            tor_nodes.append(name)
       
    # Aggr name 
    aggr_nodes = []             
    for i in xrange(0,4):
        for j in xrange(0,2):
            for k in xrange(0,2):
                name = str(2)+'_' +str(k)+'_' + str(j)+'_' +str(i)
                nodes.append(name)
                aggr_nodes.append(name)
    # Spine name
    spine_nodes = []
    for i in xrange(0,4):
        for j in xrange(0,2):
            name = str(3)+'_' +str(0)+'_' + str(j)+'_' +str(i)
            nodes.append(name)
            spine_nodes.append(name)
    
    for i in xrange(0,2):
        for j in xrange(0,2):
            name = str(3)+'_' +str(1)+'_' + str(j)+'_' +str(i)
            nodes.append(name)
            spine_nodes.append(name)
            
    return nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes

def get_nexthos_up():
    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes= getnodes()
    port_list = {}
    # Host
    for node in host_nodes:
        node_split = node.split('_')
        
        for j in xrange(0,1):
            next_hop = (str(1)
                + '_' + node_split[1]
                + '_' + node_split[2]
                + '_' +node_split[3])
            if j == 0:
                next_hop_str = next_hop
            else:
                next_hop_str += ' '+next_hop
        port_list[node] = next_hop_str
        
    # Tor
    for node in tor_nodes:
        node_split = node.split('_')
        
        for j in xrange(0,4):
            next_hop = (str(2) 
                + '_' + node_split[1]
                + '_' + node_split[2]
                + '_' +str(j))
            if j == 0:
                next_hop_str = next_hop
            else:
                next_hop_str += ' '+next_hop
        port_list[node] = next_hop_str
    
    # Aggr
    for node in aggr_nodes:
        node_split = node.split('_')
        
        if(node_split[1] == '0'):
            for j in xrange(0,2):
                next_hop = (str(2)
                    + '_' + str(1)  
                    + '_' + node_split[2]
                    + '_' + str(j+int(node_split[3])/2*2))
                if j == 0:
                    next_hop_str = next_hop
                else:
                    next_hop_str += ' ' + next_hop
        if(node_split[1] == '1'):
            for j in xrange(0,2):
                next_hop = (str(3)
                    + '_' + str(0)
                    + '_' + str(int(node_split[3])%2)
                    + '_' + str(j+int(node_split[3])/2*2))
                if j == 0:
                    next_hop_str = next_hop
                else:
                    next_hop_str += ' ' + next_hop
        port_list[node] = next_hop_str
    
    # Spine
    for node in spine_nodes:
        node_split = node.split('_')
        
        if(node_split[1] == '0'):
            for j in xrange(0,2):
                next_hop = (str(3)
                    + '_' + str(1)
                    + '_' + node_split[2]
                    + '_' + str(j))
                if j == 0:
                    next_hop_str = next_hop
                else:
                    next_hop_str += ' ' + next_hop
        
        port_list[node] = next_hop_str
    
    return port_list

def tree_topo():
    nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes = getnodes()
    next_hop_up = get_nexthos_up()

    switch_nodes = [x for x in nodes if x not in host_nodes]
    edges = []
    for key in next_hop_up.keys():
        if key not in host_nodes:
            nhops = next_hop_up[key].split()
            for nhop in nhops:
                edges.append((key, nhop))
    print(len(edges))
    external_edges = ([('3_1_0_0', 'e1'), ('3_1_0_1', 'e1'), 
                        ('3_1_1_0', 'e1'), ('3_1_1_1', 'e1')]
    )
    edges += external_edges
    return switch_nodes, edges

def mesh_topo():
    
    edges = ([('s1', 's2'), ('s1', 's5'), 
                ('s2', 's3'), ('s3', 's4'), 
                ('s3', 's6'), ('s4', 's5'), 
                ('s4', 's7'), ('s4', 's8'), 
                ('s5', 's6'), ('s6', 's7'), 
                ('s6', 's8'), ('s7', 's8'), 
                ('s7', 's11'), ('s8', 's10'), 
                ('s9', 's10'), ('s9', 's11'), 
                ('s10', 's11'), ('s10', 's12'), 
                ('s11', 's12'), 
            ]
    )
    
    host_switch = ([('s1', 'h1'), ('s2', 'h2'), 
                    ('s3', 'h3'), ('s4', 'h4'), 
                    ('s5', 'h5'), ('s6', 'h6'), 
                    ('s7', 'h7'), ('s8', 'h8'), 
                    ('s9', 'h9'), ('s10', 'h10'), 
                    ('s11', 'h11'), ('s12', 'h12')
                ]
    )
    edges += host_switch
    switches = ['s' + str(i) for i in range(1, 13)]
    
    return switches, edges
    
def blockToBlock(input_name, block_num, a0_inc, ai_inc, 
                    a0_cut=None, ai_cut=None, file_name=None, r=9):
    
    if file_name != None:
        if((os.path.isfile(file_name)) == True):
            json_data = open(file_name).read()
            edges = json.loads(json_data)
            print('len(edges)', len(edges))
            return edges
            
    # Read switches and edges from the file
    df0 = pd.read_csv(input_name, names=['a' + str(i) for i in range(r)])
    df = df0.copy()
    print df0
    
    # Generate switches and edges according to the rule: 
    # a0+a0_inc, a_i + ai_inc
    for i in range(block_num):
        df1 = df0.copy()
        df1['a0'] = df1['a0'] + a0_inc #16
        for j in range(1, r):
            df1['a' + str(j)] = df1['a' + str(j)] + ai_inc #8
        df = df.append(df1, ignore_index=True)
        df0 = df1.copy()
    
    print(df)    
    if a0_cut != None:
        df = df[df['a0'] <= a0_cut]
        
    if ai_cut != None:
        for j in range(1, r):
            df['a' + str(j)] = df['a' + str(j)][df['a' + str(j)] <= ai_cut]
    df = df.reset_index()

    edges = []
    for j in range(1, r):
        for i in range(df.shape[0]):
            if pd.isnull(df['a' + str(j)].loc[i]) == False:
                edges.append((int(df['a0'].loc[i]), int(df['a' + str(j)].loc[i])))
    print('len(edges)', len(edges))
    
    
    if file_name != None:
        with open(file_name, 'w') as file:
            file.write(json.dumps(edges))
    
    return edges

def renameSwitch(edges, prefix1, prefix2):
    """
    Rename the switch by some rules
    """
    edges_renamed = []
    for edge in edges:
        edges_renamed.append((prefix1+str(edge[0]), prefix2+str(edge[1])))
    
    return edges_renamed
    
def jupiter_topo(spine_cut=None, aggr_cut=None, tor_cut=None):
    
    """
    Build the topology with  256 spine blocks and 64 aggregation blocks,
    that is, 64*8 = 512 MBs, 
    all links: 256*16(switches)*8(links) = 512*8(switches)*8(links)
    Spine to Aggregation: all to all logically
    Each spine: 16(switches)*8(links) = 128 links
    Each aggregation: 8(MBs)*8(switches)*8(links) = 512 links
    Spine to Spine
    a0: low ai: top
    Spine to aggr
    a0: aggr_top ai: spine
    Aggr to Aggr
    a0: low ai: top
    Aggr to tor
    a0: aggr_low ai: tor
    """
    
    # Spine to Spine 4096*8
    input_name = "../inputs/spine_spine_connections.csv"
    block_num, a0_inc, ai_inc = 255, 16, 8
    file_name = '../outputs/spine_spine_edge_cut.txt'
    spine_spine_edges = blockToBlock(
            input_name, block_num, a0_inc, ai_inc, 
            a0_cut=spine_cut, ai_cut=spine_cut/2, file_name=file_name
    )
    
    prefix1, prefix2 = 'sl', 'sh'
    edges_renamed = renameSwitch(spine_spine_edges, prefix1, prefix2)
    
    # Spine to aggr 4096*8
    input_name = "../inputs/connection.csv"
    block_num, a0_inc, ai_inc = 31, 1, 128
    file_name = '../outputs/spine_aggr_edge_cut.txt'
    spine_aggr_edges = blockToBlock(
            input_name, block_num, a0_inc, ai_inc, 
            a0_cut=aggr_cut, ai_cut=spine_cut, file_name=file_name
    )
    prefix1, prefix2 = 'ah', 'sl'
    edges = renameSwitch(spine_aggr_edges, prefix1, prefix2)
    edges_renamed += edges
    print([x for x in spine_aggr_edges if x[1] == 1])
    # Aggr to Aggr 4096*8
    input_name = "../inputs/aggr_aggr_connections.csv"
    block_num, a0_inc, ai_inc = 64*8-1, 8, 8
    file_name = '../outputs/aggr_aggr_edge_cut.txt'
    aggr_aggr_edges = blockToBlock(
            input_name, block_num, a0_inc, ai_inc, 
            a0_cut=aggr_cut, ai_cut=aggr_cut, file_name=file_name
    )
    prefix1, prefix2 = 'al', 'ah'
    edges_renamed += renameSwitch(aggr_aggr_edges, prefix1, prefix2)
    
    # Aggr to tor
    input_name = "../inputs/aggr_tor_connections.csv"
    block_num, a0_inc, ai_inc = 64-1, 64, 128
    file_name = '../outputs/aggr_tor_edge_cut.txt'
    aggr_tor_edges = blockToBlock(
            input_name, block_num, a0_inc, ai_inc, 
            a0_cut=aggr_cut, ai_cut=tor_cut, file_name=file_name, r=17
    )
    prefix1, prefix2 = 'al', 'tor'
    edges_renamed += renameSwitch(aggr_tor_edges, prefix1, prefix2)
    
    # print edges_renamed
    switches = []
    
    return switches, edges_renamed

def getJupiternNodes(tors_num=8192, aggr_num=4096, spine_num=4096):
    
    nodes = []
    host_nodes, tor_nodes, aggr_nodes, spine_nodes = [], [], [], []
    # Tors
    for i in range(1, tors_num+1):
        tor_nodes.append('tor' + str(i))
    
    # Aggrs
    for i in range(1, aggr_num+1):
        aggr_nodes.append('al' + str(i))
        aggr_nodes.append('ah' + str(i))
    
    # Spines
    for i in range(1, spine_num/2+1):
        spine_nodes.append('sh' + str(i))
        
    for i in range(1, spine_num+1):
        spine_nodes.append('sl' + str(i))
    
    nodes += tor_nodes + aggr_nodes + spine_nodes
    
    return nodes, host_nodes, tor_nodes, aggr_nodes, spine_nodes

#switches, edges = jupiter_topo(tor_cut=32*4*2, aggr_cut=64*2, spine_cut=16*2)
    
    
    
    
    
