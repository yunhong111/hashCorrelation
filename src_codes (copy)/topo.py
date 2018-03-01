
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

    switch_nodes = [x for x in nodes if x not in host_nodes] + ['e1']
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
