import heapq
import pandas as pd
import numpy as np
import operator
import struct
from collections import Counter
import independent_set as iset

def dominantApp(flow_dict_per_link):
    """
    Return max key and value from the dictionary
    """
    
    return max(flow_dict_per_link.iteritems(), key=operator.itemgetter(1))

def appRatioPerLink(flow_dict_per_link, k):
    """
    k is the number of heavy hitters
    df column is the dst port
    df index is time
    """
    k_keys_sorted = heapq.nlargest(
                k, flow_dict_per_link.items(), key=operator.itemgetter(1)
    )
    #df_entry = pd.DataFrame(
        #data={struct.unpack('>I', '\x00\x00'+ x[0]):[x[1]] for x in k_keys_sorted})
    df_entry = pd.DataFrame(data={x[0]:[x[1]] for x in k_keys_sorted})
    #df_entry = df_entry.div(df_entry.sum(axis=1), axis=0)
    return df_entry

def linkRatioPerApp(flow_dict_all_link, input_node):
    """
    input_node is the number 
    """
    df = pd.DataFrame(data=flow_dict_all_link).fillna(value=0)
    
    return

def appClassification(num_cluster, inner_imr, 
        key='', imr_threshold=0.1, class_dict={}):
    # Bias
    if num_cluster > 1:
        class_dict[key] = 2
    elif num_cluster == 1 and inner_imr > imr_threshold: # Correlated
        class_dict[key] = 1
    else:
        class_dict[key] = 0
        
def appLinkCorrelation(data, perlink_df, app_link_dict, cflow_dict, 
                        key='', class_dict={}, imr_threshold=0.1,
                        k=5, topo_type='B4', links=[]
    ):
    k = 3
    if(perlink_df.shape[0] == 1):
        perlink_df.plot(x=perlink_df.index.values)
        return

    if topo_type == 'TREE':
        links = ([('2_1_0_0', '3_0_0_0'), ('2_1_0_0', '3_0_0_1')]
        )
        
    if topo_type == 'B4':
        links = ([('s4', 's7'), ('s4', 's8')])
        
    """
    next_hops = '3_0_0_0,3_0_0_1'
    next_hops = 's7,s8
    '"""
    #domi_app = ap.dominantApp(cflow_dict[link1])
    #print('    --domi_app', domi_app)
    
    x = app_link_dict

    # The top k app on switch
    df_entry = None
    for link in links:
        if link not in x:
            x[link] = {}
        if df_entry == None:
            df_entry = Counter(x[link])
        else:
            df_entry += Counter(x[link])
            
    df_entry = appRatioPerLink(
                df_entry, k
    )
    
    top_apps = list(df_entry.columns.values)
    app_link_table = []
    link_topk = 1
    link_bottomk = 1
    for app in top_apps:
        #app = struct.pack('>I', app)[2:]
        tmp = []
        for link in links:
            if app in x[link]:
                print x[link][app],
                tmp.append(x[link][app])
            else:
                x[link][app] = 0.1
                print 0,
                tmp.append(0.1)
        print '\n'
        tmp = sorted(tmp)
        print 'tmp', tmp
        app_link_table.append(tmp[0:link_topk]+tmp[-link_bottomk:])
    app_link_table = np.transpose(np.array(app_link_table))
    app_df = pd.DataFrame(
        app_link_table, columns=['a' + str(x) for x in top_apps])
    print app_df
    app_imrs = iset.independentCluster(app_df, 0.01)
    
    perlink_df = perlink_df.append(
                df_entry, ignore_index=True).fillna(value=0
    )
    appClassification(
        len(app_imrs), app_imrs[0][2], 
        key=key, imr_threshold=imr_threshold, class_dict=class_dict)
    
    inner_imr = app_imrs[0][2]
    print('    --df_entry', df_entry)
    return [x[2] for x in app_imrs]

