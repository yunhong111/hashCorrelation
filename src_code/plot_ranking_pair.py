
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plot_lib as pl
from collections import OrderedDict
import co_func as cf
from collections import OrderedDict

def init_files(trace_type = ' ', task_type='CLASSIFICATION', topo_type='b4', 
                x_var = 'FLOWNUM', p=0.01
    ):
    file_name1, file_name2 = cf.init_files(trace_type=trace_type, 
                task_type=task_type, topo_type=topo_type, 
                x_var=x_var, p=p)
            
    return file_name1, file_name2    
        
def read_csv(file_name, file_type=0, topo_type='CLASSIFICATION', is_epsilon=False):
    global ACAP

    if file_type == 0:
        return pd.read_csv(file_name)
    else:
        print('here')
        names=['#flows', 'epsilon', 'is_correlated', 'key', '#pres', 'o_f'] + ['a' + str(i) for i in range(ACAP)]
        if is_epsilon:
            names=['#flows', 'epsilon', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        return pd.read_csv(file_name, skiprows=[0], names=names)

def q1(x):
    return x.quantile(0.25)

def q2(x):
    return x.quantile(0.75)
    
def ranking_num(row):
    global ACAP

    num = 0
    for i in range(ACAP):
        if isinstance(row['a'+str(i)], str)  and 'end' in row['a'+str(i)]:
            num = i/2
            break
    if num == 0:
        print row
        print('ranking_num:num==0')
        eeeee
    return num
    
def rankingPair(infile_name, cherns, flow_seq, pair_seqs, 
                file_type=0, topo_type='CLASSIFICATION', cut=None, 
                q_25s=[], q_75s=[]
    ):
    # d: key: ranking[]
    df1 = read_csv(infile_name, file_type, topo_type=topo_type)
    df1 = df1.replace([2, '2.0', 2.0, '2'], 1)
    df1 = df1.fillna(value='end')

    d = OrderedDict({})
    print df1['key'].unique()
    
    print df1
    pvalues_d = OrderedDict({}) 
    for flow_num in df1['#flows'].unique():
        for key in df1['key'].unique():
            if (str(flow_num)+key) not in d:
                d[str(flow_num)+key] = OrderedDict({})
                pvalues_d[str(flow_num)+key] = OrderedDict({})
               
    for index, row in df1.iterrows():
        num = ranking_num(row)
        key = str(row['#flows'])+row['key']
        for i in range(num):
            if row['a'+str(num+i)] not in d[key]:
                d[key][row['a'+str(num+i)]] = [0, 0]
                pvalues_d[key][row['a'+str(num+i)]] = []
            d[key][row['a'+str(num+i)]][0] +=  float(row['a'+str(i)])
            d[key][row['a'+str(num+i)]][1] +=  1
            pvalues_d[key][row['a'+str(num+i)]].append(float(row['a'+str(i)]))
    
    d1 = OrderedDict({})
    pvaluess = OrderedDict({})
    for key1 in d:
        d1[key1] = []
        pvaluess[key1] = []
        for key2 in d[key1]:
            d[key1][key2][0] /= d[key1][key2][1]
            d1[key1].append((d[key1][key2][0], key2))
            
            x = np.mean(pvalues_d[key][key2])
            q_25 = np.percentile(x-pvalues_d[key][key2], 0.25)
            q_75 = np.percentile(pvalues_d[key][key2]-x, 0.75)
            pvaluess[key1].append((x, q_25, q_75))
        d1[key1] = sorted(d1[key1], key=lambda tup: tup[0])
    
    for pair_seq in pair_seqs:
        pair = str(df1['#flows'].unique()[flow_seq])+df1['key'].unique()[pair_seq]

        if cut == None:
            cherns.append([x[0]for x in d1[pair]])
            
            x = [x[1] for x in d1[pair]]
        else:
            cherns.append([x[0]for x in d1[pair][:cut]])
            
            q_25s.append([x[1] for x in pvaluess[pair][:cut]])
            q_75s.append([x[2] for x in pvaluess[pair][:cut]])
            x = [x[1] for x in d1[pair][:cut]]
            
    
    return x
    

def rankingPlot(topo_types, task_types, trace_types, pair_seq=0):
    global ACAP
    
    accuracys, errors, x, q_75s, q_25s = [], [], None, [], []
    cherns, chern_errors, chern_x = [], [], None
    
    for topo_type in topo_types[1:2]:
        trace_type = trace_types[0]
        task_type = task_types[1]
        cut = 4
        if topo_type == topo_types[2]:
            ACAP = 256
            cut = 10
        
        infile_name1, infile_name2 = init_files(
                                    trace_type, task_type, topo_type
        )

        group_fields = ['#flows','is_correlated', 'key']
        agg_fields = ['a'+str(i) for i in range(ACAP)]

        chern_x = rankingPair(
            infile_name2, cherns, 0, [0, 1], 
            file_type=1, topo_type=topo_type, cut=cut, q_25s=q_25s, q_75s=q_75s
        )
    
    xlabel, ylabel = 'Rank', 'Average p-value'

    xticks = []
    if chern_x != None:
        xticks = chern_x
        
    print chern_x, cherns
    pl.plot(cherns, x=None, k=2, errors=[q_25s, q_75s], 
        xlabel=xlabel, ylabel=ylabel, 
        title=infile_name1.split('/outputs')[1].split('.csv')[0]+'pair-key'+str(pair_seq), 
        xlog=False, ylog=True, acc_legend=['0-hop', '1-hop'], xticks=np.arange(1, cut+1),
        figure_width=4.3307, figure_height=3.346, x_shift=0.06, y_shift=0.05
    )
    
if __name__ == "__main__":
    global ACAP
    ACAP = 50
    topo_types = ['B4', 'TREE', 'JUPITER']
    task_types = ['CLASSIFICATION', 'RANKING', 'APPLICATION']
    trace_types = ['A', 'B', 'C', 'e1', 'e5', 'e10', 'e50', 'e100']
    pair_seq = 1
    print trace_types[:3]
    #accuracyPlot(topo_types, task_types, trace_types[:3], pair_seq=pair_seq)
    rankingPlot(topo_types, task_types, trace_types[:3], pair_seq=pair_seq)
    
    plt.show()
