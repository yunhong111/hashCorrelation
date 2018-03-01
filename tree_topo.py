import networkx as nx
import matplotlib.pyplot as plt
from crc8 import crc8
from co_func import append_path
import random
from path_matrix import path_matrix
import mesh_detection as mdt
import topo
import multiprocessing as mp

def get_seeds_table(router_nodes):
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
        seeds[node] = i*7%255
        if i < np:
            polys[node] = poly_list[i]
        else:
            k = random.randint(0, np-1)
            polys[node] = poly_list[k]
        i += 1
    
    """
    polys = ({'s3': 0x31, 's4': 0x2f, 's5': 0x39, 
        's6': 0xd5, 's7': 0x4d, 's8': 0x8d, 
        's10': 0x9b, 's11': 0x7a, 's1': 0x07, 
        's2': 0x07, 's9': 0x07, 's12': 0x07}
    )
    """
    
    return seeds, polys

def set_correlation(r1, r2, polys):
    poly_r2 = polys[r2]
    polys[r2] = polys[r1]
    return poly_r2

def reset_correlation(r2, polys, poly):
    polys[r2] = poly
    
def build_graph(edges):
    G = nx.MultiGraph()
    """
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
    """
    
    G.add_edges_from(edges)
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
    if cur_hop == d:
        append_path(hash_str, cur_hop, flow_paths)
        return 
        
    append_path(hash_str, cur_hop, flow_paths)
    nhop = table[cur_hop][d][0]
    n = len(table[cur_hop][d])
    if n > 1:
        ni = crc8(seeds[cur_hop], hash_str, polys[cur_hop])%n
        nhop = table[cur_hop][d][ni]
    next_hop(nhop, cur_hop, s, d, hash_str, table, seeds, polys, flow_paths)

def map_addr_tree(s, d, tors):
    """
    Map the current source and dest address to the ones in the topo
    """
    n = len(tors)
    
    s_out = crc8(0, s, 0x31)%n
    tor_ds = tors[:s_out] + tors[s_out+1 :]
    nd = n - 1
    d_out = crc8(0, d, 0x1d)%nd
    s_out, d_out = tors[s_out], tor_ds[d_out]
    
    return s_out, d_out
    
def flow_routing(file_name, seeds, polys, flow_paths, tors):
    
    count = 0;
    start_time = 0;
    is_update = True
    
    with open((file_name), 'r') as f:
        for line in f:
            count += 1
            if(count < 15000):
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
                  
                hash_str = (data[2]
                        + '\t' + data[3]
                        + '\t' + data[4]
                        + '\t' + data[5]
                        + '\t' + data[6]
                )
                s, d = map_addr_tree(data[2], data[3], tors)    

                next_hop(
                    s, 'h1', s, d, hash_str, table, seeds, polys, flow_paths
                )
            else:
                print((float(data[0]) - start_time))
                break                

def single(r1, r2, pairs, switch_nodes, trues, ests, tors):
    
    poly = set_correlation(r1, r2, polys)
    
    flow_paths = {}
    flow_routing(file_name, seeds, polys, flow_paths, tors)
    
    rm = path_matrix(flow_paths, switch_nodes)
    print(len(rm))
    
    cherns = {}
    dss = []
    for s in switch_nodes:
        cherns[s], ds = mdt.hash_biased(s, rm, switch_nodes, table[s])
        dss.append(ds)
    print('cherns', cherns)
    
    epsilon = 0.02
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

def single_mul(r1, r2, switch_nodes, tors):
    
    pairs, trues, ests = [], 0, 0
    poly = set_correlation(r1, r2, polys)
    
    flow_paths = {}
    flow_routing(file_name, seeds, polys, flow_paths, tors)
    
    rm = path_matrix(flow_paths, switch_nodes)
    print(len(rm))
    
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
            
            """ranking = locate_corr(s, rm, switch_nodes, table)
            print('ranking', ranking)
            if len(ranking) != 0:
                if ranking[0][0] == r1 or ranking[0][0] == r2:
                    ests += 1
                    """
            
    reset_correlation(r2, polys, poly)
    return pairs, trues, ests

def locate_corr(s, rm, switch_nodes, table):
    #
    pre_hops = [x for x in switch_nodes if x != s]
    print('pre_hops', pre_hops)
    cherns = mdt.corr_group(s, rm, switch_nodes, table)
    return cherns

if __name__ == "__main__":
    
    nodes, host_nodes, tors, aggr_nodes, spine_nodes = topo.getnodes()
    print(tors)
    # Build a graph
    switch_nodes, edges = topo.tree_topo()
    G = build_graph(edges)
       
    # Get the routing path of all nodes
    sd_switches = tors + ['e1']
    table = all_routing(G, sd_switches)

    seeds, polys = get_seeds_table(switch_nodes)
    print('polys', polys)
    file_name = ("/home/yunhong/Research_4/distributions/outputs/"
                + "split_flows_150s_web_sort_host"
    )
    
    test_pairs = [['1_0_0_0', '2_0_0_1', 0.014843329184995955], ['1_0_1_0', '2_0_1_1', 0.011017503181739042], ['1_0_1_0', '2_0_0_2', 0.0077203599636126], ['1_0_1_0', '2_0_1_3', 4.768601237005852e-05], ['1_0_0_1', '2_0_1_2', 0.01875079753171262], ['1_0_1_1', '2_0_1_2', 0.0009950025277969377], ['1_0_1_1', '3_0_1_0', 0.001782756858482295], ['1_0_0_2', '2_0_0_0', 0.014469568097484285], ['1_0_1_2', '2_0_1_2', 0.003269660665491937], ['1_0_0_3', '2_0_0_2', 0.011317166478674765], ['1_0_0_4', '2_0_1_1', 0.006575482134629476], ['1_0_0_4', '2_1_1_2', 0.019309148353160877], ['1_0_1_4', '2_0_1_0', 0.008823337526455166], ['1_0_1_4', '2_0_1_2', 0.002227400962177827], ['1_0_0_5', '2_0_0_1', 0.007650936345479383], ['1_0_0_5', '2_0_0_3', 0.01875079753171262], ['1_0_0_5', '2_1_0_3', 0.006782844798571482], ['1_0_0_5', '2_1_1_3', 0.009996643189105292], ['1_0_0_5', '3_1_0_0', 0.012937571574704602], ['1_0_0_5', '3_1_0_1', 0.015304965652761833], ['1_0_1_5', '2_0_1_0', 0.003074611568457446], ['1_0_1_5', 'e1', 1.7918771160383572e-07], ['1_0_1_5', 'e1', 0.010247624760693129], ['1_0_0_6', '2_0_0_0', 0.0003137687627595209], ['1_0_0_6', '2_0_1_2', 0.005024258187251243], ['1_0_0_6', '2_0_0_3', 0.007300945545570229], ['1_0_1_6', '2_0_1_1', 0.0028779718162542816], ['1_0_0_7', '2_0_0_1', 0.005392638807101466], ['1_0_0_7', '2_1_0_2', 0.016237898230125853], ['1_0_1_7', '2_0_1_0', 0.000637305877178869], ['2_0_0_0', '1_0_0_1', 5.1807241994341084e-05], ['2_0_0_0', '1_0_0_3', 3.704585047817662e-05], ['2_0_0_0', '1_0_0_6', 6.66605469472107e-05], ['2_1_0_0', '3_0_0_0', 0.012955862044255997], ['2_0_1_0', '1_0_1_4', 0.015994449589385066], ['2_0_1_0', '1_0_1_5', 0.0035103347732294956], ['2_0_1_0', '3_0_0_1', 0.0004425180062028879], ['2_1_1_0', '1_0_1_1', 0.010877396916613807], ['2_1_1_0', '3_0_0_0', 0.00010659880303906092], ['2_1_1_0', '3_0_0_1', 1.2983318764544258e-05], ['2_1_1_0', 'e1', 1.342392074493482e-06], ['2_0_0_1', '1_0_0_3', 0.016340720849598624], ['2_0_0_1', '1_0_1_3', 0.017498365757249477], ['2_0_0_1', '1_0_0_5', 0.010145251394522325], ['2_1_0_1', '3_0_1_0', 0.0004529288965168041], ['2_1_0_1', '3_0_1_1', 0.0001701626564420784], ['2_0_1_1', '1_0_1_0', 0.007056460722044756], ['2_0_1_1', '1_0_1_1', 0.014986302155260025], ['2_0_1_1', '1_0_1_4', 0.010358439458259774], ['2_0_1_1', '1_0_0_6', 0.01765319054623149], ['2_0_1_1', '3_0_0_1', 0.019887515223864168], ['2_1_1_1', '3_0_1_1', 3.400026679241347e-05], ['2_0_0_2', '1_0_0_0', 0.012141360532151022], ['2_0_0_2', '1_0_0_6', 0.01560579211527575], ['2_1_0_2', '1_0_1_2', 0.013378414773137583], ['2_1_0_2', '3_0_0_2', 0.004909353831590503], ['2_0_1_2', '1_0_1_0', 0.011150934458060521], ['2_0_1_2', '1_0_1_1', 0.002653777514925275], ['2_0_1_2', '1_0_1_3', 0.006782844798571482], ['2_0_1_2', '1_0_0_5', 0.011661349825314152], ['2_0_1_2', '1_0_1_5', 0.0004231174798753874], ['2_0_1_2', '1_0_1_7', 0.0031727711944911042], ['2_0_1_2', '3_0_1_2', 0.015207217168300636], ['2_1_1_2', '3_0_0_2', 0.004909353831590503], ['2_1_1_2', '3_0_0_3', 0.01875079753171262], ['2_0_0_3', '1_0_0_1', 0.004711848431401109], ['2_0_0_3', '1_0_1_1', 0.006994065178650931], ['2_0_0_3', '1_0_0_3', 0.010139095493652002], ['2_0_0_3', '3_0_1_3', 0.002783975507679347], ['2_1_0_3', '3_0_1_2', 0.0046521418458778455], ['2_1_0_3', '3_0_1_3', 0.009011684247904977], ['2_0_1_3', '1_0_1_1', 0.011499827209099152], ['2_0_1_3', '1_0_1_2', 0.013024804107429405], ['2_0_1_3', '1_0_1_5', 0.013506850076008374], ['2_0_1_3', '1_0_1_5', 0.00139921633544633], ['2_0_1_3', '3_0_1_0', 0.0173193791048939], ['2_1_1_3', '3_0_1_2', 0.0046521418458778455], ['2_1_1_3', '3_1_0_0', 3.189156292949127e-08], ['2_1_1_3', '3_1_1_0', 1.7898560993246426e-06], ['2_1_1_3', '3_1_0_1', 2.389169488051143e-07], ['2_1_1_3', '3_1_1_1', 4.2522083905988365e-08], ['3_0_0_0', '1_0_1_1', 0.014843329184995955], ['3_0_0_0', '2_1_0_0', 0.011808968350121107], ['3_0_0_0', '2_1_1_0', 0.004728625646825337], ['3_0_1_0', '2_1_0_1', 0.0029646732290575174], ['3_0_1_0', 'e1', 5.669611187465115e-08], ['3_0_0_1', '1_0_1_4', 0.01875079753171262], ['3_0_0_1', '2_1_1_0', 0.0011847450298244605], ['3_0_1_1', '2_1_1_1', 0.001782756858482295], ['3_0_1_1', '2_1_0_3', 0.011150934458060521], ['3_0_0_2', '2_1_1_2', 0.017009314318280178], ['3_0_1_2', '2_0_0_3', 0.010086721881892349], ['3_0_1_2', '2_1_0_3', 3.400026679241347e-05], ['3_0_1_2', 'e1', 0.015510546767196294], ['3_0_0_3', '1_0_1_1', 0.013378414773137583], ['3_0_0_3', '1_0_1_4', 0.01875079753171262], ['3_0_0_3', '2_0_1_2', 0.0011474988053136977], ['3_0_0_3', '2_1_1_2', 7.001982897797315e-05], ['3_0_0_3', '2_0_0_3', 0.005024258187251243], ['3_0_1_3', '1_0_1_2', 0.010158380498301166], ['3_0_1_3', '2_0_1_3', 0.0173193791048939], ['3_0_1_3', '2_1_1_3', 9.64348345576088e-05], ['3_1_0_0', '1_0_1_1', 0.009313240101037281], ['3_1_0_0', '1_0_1_2', 0.0064257645860808675], ['3_1_0_0', '1_0_1_2', 0.016666581984427765], ['3_1_0_0', '1_0_1_7', 0.016666581984427765], ['3_1_0_0', 'e1', 4.247412423202032e-07], ['3_1_1_0', '1_0_1_1', 0.011818211452173804], ['3_1_1_0', '1_0_1_3', 0.017986653374705154], ['3_1_1_0', '2_0_1_0', 0.003074611568457446], ['3_1_1_0', 'e1', 1.7918771160383572e-07], ['3_1_1_0', 'e1', 0.010247624760693129], ['3_1_0_1', '2_1_0_1', 0.0029646732290575174], ['3_1_0_1', 'e1', 5.669611187465115e-08], ['3_1_1_1', '1_0_1_1', 0.010877396916613807], ['3_1_1_1', '2_0_0_0', 1.0320654602621072e-18], ['3_1_1_1', '2_0_1_0', 4.169311574353556e-21], ['3_1_1_1', '2_0_0_1', 7.11294883827635e-19], ['3_1_1_1', '2_0_1_1', 3.3999871069665916e-15], ['3_1_1_1', 'e1', 1.342392074493482e-06], ['e1', '2_0_0_2', 1.9307228412234663e-25], ['e1', '2_0_1_2', 5.289061218227099e-17], ['e1', '2_0_0_3', 1.1425563453806146e-10], ['e1', '2_0_1_3', 1.6974266219110103e-20], ['e1', '3_0_1_2', 0.0046521418458778455], ['e1', '3_1_0_0', 3.189156292949127e-08], ['e1', '3_1_1_0', 1.7898560993246426e-06], ['e1', '3_1_0_1', 2.389169488051143e-07], ['e1', '3_1_1_1', 4.2522083905988365e-08]]
    pairs = []
    trues, ests = 0, 0
    for tup in test_pairs: #['3_0_0_0']: #
        r1, r2 = tup[0], tup[1]
        if r1 != r2 and r1[0:2] != r2[0:2]:
            a = 0
            trues, ests = single(
                            r1, r2, pairs, switch_nodes, 
                            trues, ests, sd_switches
            )
    print('pairs', pairs)
    
    #trues, ests = single('s4', 's3', pairs, switch_nodes, trues, ests)
    print('trues, ests', trues, ests)
    #mdt.corr_group(['s4'], 's3', rm, switch_nodes, table)
    #mdt.corr_group(['s3'], 's4', rm, switch_nodes, table)
    
    
