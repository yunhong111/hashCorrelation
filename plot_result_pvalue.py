
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plot_lib as pl
from collections import OrderedDict
from sklearn.metrics import accuracy_score

def init_files(trace_type = ' ', task_type='CLASSIFICATION', topo_type='b4', 
                x_var = 'FLOWNUM'
    ):
    infile_name1 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_trace'+trace_type+'.csv')
    infile_name2 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_chern_trace'+trace_type+'.csv')
            
    return infile_name1, infile_name2        
        
def read_csv(file_name, file_type=0, topo_type='CLASSIFICATION', is_epsilon=False):
    global ACAP

    if file_type == 0:
        names=(['#flows', 'epsilon', 'is_correlated', 
                'key', 'count_chern', 'byte_chern', 'class']
        )
        return pd.read_csv(file_name, skiprows=[0], names=names)
    else:
        print('here')
        names=['#flows', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        if is_epsilon:
            names=['#flows', 'epsilon', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        return pd.read_csv(file_name, skiprows=[0], names=names)

def retieveData(infile_name1, group_fields, agg_fields, 
                accuracys, errors, div=False, 
                task_type="CLASSIFICATION", file_type=0, 
                iteration=10, pair_num=4
    ):
    
    df1 = read_csv(infile_name1, file_type)
    df1 = df1.replace([2, '2.0', 2.0, '2'], 1)
    df1['true'] = df1['is_correlated'].replace([0], -1)
    df1['colFromIndex'] = df1.index
    df1 = df1.sort(columns=['epsilon', 'colFromIndex'])

    df1 = df1.reset_index()
    pvalue_num = df1['epsilon'].unique().shape[0]
    group_num = pair_num*2
    acc_dict = OrderedDict({})
    for i in range(iteration*pvalue_num):
        s_index = i*group_num
        e_index = (i+1)*group_num - 1
        if df1['epsilon'].loc[s_index] != df1['epsilon'].loc[e_index]:
            print df1.loc[s_index], df1.loc[e_index]
            eeee
        key = df1['epsilon'].loc[e_index]
        y_pred = df1['class'].loc[s_index:e_index]
        y_true = df1['true'].loc[s_index:e_index]
        acc = accuracy_score(y_true, y_pred)
        if key not in acc_dict:
            acc_dict[key] = []
        acc_dict[key].append(acc)
        print len(y_pred), df1['epsilon'].unique()
    print acc_dict
    accuracy = []
    error = []
    for key in acc_dict:
        accuracy.append(np.mean(acc_dict[key]))
        error.append(np.std(acc_dict[key]))
    accuracys.append(accuracy)
    errors.append(error)
    print acc_dict
    
    return df1['epsilon'].unique(), pvalue_num, acc_dict
    
def accuracyPlot(topo_types, task_types, trace_types, pair_seq=0):
    
    accuracys, errors, x = [], [], None
    cherns, chern_errors, chern_x = [], [], None
    acc_boxplot_data = []
    
    for trace_type in trace_types:
        topo_type = topo_types[2]
        task_type = task_types[0]
        if topo_type == topo_types[0]:
            pair_num = 4
        elif topo_type == topo_types[1]:
            pair_num = 8
        elif topo_type == topo_types[2]:
            pair_num = 14
        
        infile_name1, infile_name2 = init_files(
                                    trace_type, task_type, topo_type,
                                    x_var = 'PVALUE'
        )
        
        group_fields = ['#flows','is_correlated', 'key']
        agg_fields = ['count_chern', 'byte_chern']
        chern_x, case_num, acc_dict = retieveData(
                infile_name2, group_fields, agg_fields, 
                accuracys, errors, div=False, pair_num=pair_num
        )
        acc_boxplot_data.append(acc_dict.values())
    
    acc_legend = ['Database', 'Web', 'Hadoop']
    xlabel, ylabel = 'The threshold for p-value', 'Average accuracy'
    print accuracys, chern_x
    pl.plot(accuracys, x=chern_x, k=2, errors=errors, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1, 
        xlog=False, ylog=False, acc_legend=acc_legend,
        legend_y=0.85
    )
    print acc_boxplot_data
    
    pl.box_plot([acc_boxplot_data[0]], x=chern_x, k=2, errors=errors, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1, 
        xlog=False, ylog=False, acc_legend=acc_legend,
        legend_y=0.85, xticks=[str(i) for i in chern_x])

    
if __name__ == "__main__":
    global ACAP
    ACAP = 50
    topo_types = ['B4', 'TREE', 'JUPITER']
    task_types = ['CLASSIFICATION', 'RANKING', 'APPLICATION']
    trace_types = ['A', 'B', 'C']
    pair_seq = 13
    accuracyPlot(topo_types, task_types, trace_types, pair_seq=pair_seq)
    plt.show()
