
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plot_lib as pl
from collections import OrderedDict

def init_files(trace_type = ' ', task_type='CLASSIFICATION', topo_type='b4', 
                x_var = 'FLOWNUM'
    ):
    file_name1 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_trace'+trace_type+'.csv')
    file_name2 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_chern_trace'+trace_type+'.csv')
            
    return file_name1, file_name2    
        
def read_csv(file_name, file_type=0, topo_type='CLASSIFICATION', is_epsilon=False):
    global ACAP

    if file_type == 0:
        return pd.read_csv(file_name)
    else:
        print('here')
        names=['#flows', 'epsilon', 'is_correlated', 'key', '#pres'] + ['a' + str(i) for i in range(ACAP)]
        if is_epsilon:
            names=['#flows', 'epsilon', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        return pd.read_csv(file_name, skiprows=[0], names=names)

def retieveData(infile_name1, group_fields, agg_fields, 
                accuracys, errors, div=False, 
                task_type="CLASSIFICATION", file_type=0
    ):
    
    df1 = read_csv(infile_name1, file_type)
    df1 = df1.replace([2, '2.0', 2.0, '2'], 1)
    flow_nums = df1['#flows'].unique()

    if div == True:
        if task_type == "CLASSIFICATION":
            case_num = df1['#all_cases'].loc[0]
        else:
            case_num = df1['#correlated_detect'].max()
    else:
        case_num = 1
    df1 = df1[df1['is_correlated'] == 1]
    agg_dict = OrderedDict({})
    for agg_field in agg_fields:
        agg_dict[agg_field] = ['mean', 'std']
        
    df1 = (df1
            .groupby(group_fields)
            .agg(agg_dict)
    )
        
    data = df1[agg_fields[0]]['mean'].divide(case_num)
    error = df1[agg_fields[1]]['std'].divide(case_num)

    accuracys.append(data)
    errors.append(error)

    #[x[0] for x in df1.index.values]
    return flow_nums, case_num

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
    
def rankingPair(infile_name, cherns, flow_seq, pair_seq, 
                file_type=0, topo_type='CLASSIFICATION', cut=None
    ):
    # d: key: ranking[]
    df1 = read_csv(infile_name, file_type, topo_type=topo_type)
    df1 = df1.replace([2, '2.0', 2.0, '2'], 1)
    df1 = df1.fillna(value='end')

    d = {}
    print df1['key'].unique()
    
    print df1
    for flow_num in df1['#flows'].unique():
        for key in df1['key'].unique():
            print flow_num, key
            if (str(flow_num)+key) not in d:
                d[str(flow_num)+key] = {}
                
    for index, row in df1.iterrows():
        num = ranking_num(row)
        key = str(row['#flows'])+row['key']
        for i in range(num):
            if row['a'+str(num+i)] not in d[key]:
                d[key][row['a'+str(num+i)]] = [0, 0]
            d[key][row['a'+str(num+i)]][0] +=  float(row['a'+str(i)])
            d[key][row['a'+str(num+i)]][1] +=  1
    
    d1 = {}
    for key1 in d:
        d1[key1] = []
        for key2 in d[key1]:
            d[key1][key2][0] /= d[key1][key2][1]
            d1[key1].append((d[key1][key2][0], key2))
        d1[key1] = sorted(d1[key1], key=lambda tup: tup[0])
    pair = str(df1['#flows'].unique()[flow_seq])+df1['key'].unique()[pair_seq]
    print pair
    print d1[pair]

    if cut == None:
        cherns.append([x[0]for x in d1[pair]])
        x = [x[1] for x in d1[pair]]
    else:
        cherns.append([x[0]for x in d1[pair][:cut]])
        x = [x[1] for x in d1[pair][:cut]]
    
    return x
    
def accuracyPlot(topo_types, task_types, trace_types, pair_seq=0):
    
    accuracys, errors, x = [], [], None
    cherns, chern_errors, chern_x = [], [], None
    
    for trace_type in trace_types:
        topo_type = topo_types[0]
        task_type = task_types[1]
        
        infile_name1, infile_name2 = init_files(
                                    trace_type, task_type, topo_type
        )
        group_fields = ['#flows','is_correlated']
        agg_fields = ['#correlated_detect', '#non-uniform_detect']
        x, case_num = retieveData(
                infile_name1, group_fields, agg_fields, 
                accuracys, errors, div=True
        )
        print x, case_num
        
        group_fields = ['#flows','is_correlated', 'key']
        agg_fields = ['count_chern', 'byte_chern']
        chern_x = retieveData(
                infile_name2, group_fields, agg_fields, 
                cherns, chern_errors, div=False
        )
    
    acc_legend = ['Database', 'Web', 'Hadoop', 'e1', 'e5', 'e10', 'e50', 'e100']
    xlabel, ylabel = 'The number of flows', 'Average accuracy'

    pl.plot(accuracys, x=x, k=2, errors=errors, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1.split('.')[0], 
        xlog=False, ylog=False, acc_legend=acc_legend[0:3]
    )
    
    """xlabel, ylabel = 'The number of flows', 'Average p-value'
    
    chern_x_pair = chern_x[0][0::case_num]
    cherns_per_pair = []
    cherns_error_pair = []

    for j in range(len(cherns)):
        for i in range(pair_seq,pair_seq+1):
            key = cherns[j].index.values[i][2]
            cherns_per_pair.append(cherns[j][i::case_num])
            cherns_error_pair.append(chern_errors[j][i::case_num])
    print cherns_per_pair, chern_x_pair
    pl.plot(cherns_per_pair, x=chern_x_pair, k=2, errors=[], 
        xlabel=xlabel, ylabel=ylabel, 
        title=infile_name1.split('.')[0]+'pair-key'+str(pair_seq), 
        xlog=False, ylog=True, acc_legend=acc_legend, legend_y=0.85
    )"""

def rankingPlot(topo_types, task_types, trace_types, pair_seq=0):
    global ACAP
    
    accuracys, errors, x = [], [], None
    cherns, chern_errors, chern_x = [], [], None
    
    for trace_type in trace_types:
        topo_type = topo_types[0]
        task_type = task_types[1]
        cut = 5
        if topo_type == topo_types[2]:
            ACAP = 256
            cut = 10
        
        infile_name1, infile_name2 = init_files(
                                    trace_type, task_type, topo_type
        )
        group_fields = ['#flows','is_correlated']
        agg_fields = ['#correlated_detect', '#correlated_detect']
        x, case_num = retieveData(
                infile_name1, group_fields, agg_fields, 
                accuracys, errors, div=True, task_type='RANKING'
        )
        print(len(x))
        group_fields = ['#flows','is_correlated', 'key']
        agg_fields = ['a'+str(i) for i in range(ACAP)]
        #print(agg_fields)
        chern_x = rankingPair(
            infile_name2, cherns, 4, pair_seq, 
            file_type=1, topo_type=topo_type, cut=cut
        )
    
    acc_legend = ['Database', 'Web', 'Hadoop', 'e1', 'e5', 'e10', 'e50', 'e100']
    xlabel, ylabel = 'The number of flows', 'Average accuracy'
    pl.plot(accuracys, x=x, k=2, errors=errors, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1.split('.')[0], 
        xlog=False, ylog=False, acc_legend=acc_legend[:3]
    )
    
    xlabel, ylabel = 'Previous hop', 'Average p-value'
    print chern_x
    xticks = []
    if chern_x != None:
        xticks = chern_x
    pl.plot(cherns, x=None, k=len(cherns), errors=[], 
        xlabel=xlabel, ylabel=ylabel, 
        title=infile_name1.split('.')[0]+'pair-key'+str(pair_seq), 
        xlog=False, ylog=True, acc_legend=acc_legend, xticks=chern_x,
        figure_width=4.3307*1.25
    )
    
if __name__ == "__main__":
    global ACAP
    ACAP = 50
    topo_types = ['B4', 'TREE', 'JUPITER']
    task_types = ['CLASSIFICATION', 'RANKING', 'APPLICATION']
    trace_types = ['A', 'B', 'C', 'e1', 'e5', 'e10', 'e50', 'e100']
    pair_seq = 2
    print trace_types[:3]
    #accuracyPlot(topo_types, task_types, trace_types[:3], pair_seq=pair_seq)
    rankingPlot(topo_types, task_types, trace_types[:3], pair_seq=pair_seq)
    
    plt.show()
