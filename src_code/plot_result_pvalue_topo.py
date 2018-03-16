
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plot_lib as pl
from collections import OrderedDict
from sklearn.metrics import accuracy_score
import co_func as cf

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
        names=(['#flows', 'epsilon', 'is_correlated', 
                'key', 'count_chern', 'byte_chern', 'class']
        )
        return pd.read_csv(file_name)
    else:
        print('here')
        names=['#flows', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        if is_epsilon:
            names=['#flows', 'epsilon', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        return pd.read_csv(file_name, skiprows=[0], names=names)

def retieveData(infile_name1, group_fields, agg_fields, 
                accuracys, errors, div=False, 
                task_type="CLASSIFICATION", file_type=0, 
                iteration=10, pair_num=4, key_field='epsilon', q_75ss=[]
    ):
    print infile_name1
    df1 = read_csv(infile_name1, file_type)
    df1 = df1.replace([2, '2.0', 2.0, '2'], 1)
    df1.loc[df1['is_correlated']==1, 'true'] = 1
    #print df1
    #df1['true'] = df1['is_correlated'].replace([0], -1)
    df1['colFromIndex'] = df1.index
    df1 = df1.sort(columns=[key_field, 'colFromIndex'])
    df1_part1 = df1[df1['is_correlated'] == 0]
    df1_part2 = df1[df1['is_correlated'] == 1]
    print df1_part1
    print df1.groupby([key_field]).count()

    df1 = df1.reset_index()
    df1_part1 = df1_part1.reset_index()
    df1_part2 = df1_part2.reset_index()

    pvalue_num = df1[key_field].unique().shape[0]
    group_num = pair_num
    acc_dict = OrderedDict({})
    for i in range(iteration*pvalue_num):
        s_index = i*group_num*3
        e_index = (i+1)*group_num*3 - 1
        print 'index', s_index, e_index, len(df1), group_num, iteration*pvalue_num

        #if e_index <= len(df1)+1:
        if df1[key_field].loc[s_index] != df1[key_field].loc[e_index]:
            print df1.loc[s_index], df1.loc[e_index]
            eeee
        key = df1[key_field].loc[e_index]

        y_pred = df1['pred'].loc[s_index:e_index]
        #y_pred = y_pred.append(df1_part2['pred'].loc[s_index:e_index])
        y_true = df1['true'].loc[s_index:e_index]
        #y_true = y_true.append(df1_part2['true'].loc[s_index:e_index])
        acc = accuracy_score(y_true, y_pred)
        if key not in acc_dict:
            acc_dict[key] = []
        acc_dict[key].append(acc)

    print len(acc_dict)

    accuracy = []
    error = []
    q_25s = []
    q_75s = []
    for key in acc_dict:
        df = pd.DataFrame(acc_dict[key], columns=['key'])
        x= df['key'].mean()
        accuracy.append(x)
        q_25 = df['key'].quantile(0.25)
        q_75 = df['key'].quantile(0.75)
        error.append(np.std(acc_dict[key]))
        q_25s.append(x-q_25)
        q_75s.append(q_75-x)

    accuracys.append(accuracy)
    errors.append(error)
    q_75ss.append([q_25s, q_75s])
    
    return df1[key_field].unique(), pvalue_num, acc_dict
    
def accuracyPlot(topo_types, task_types, trace_types, pair_seq=0):
    
    accuracys, errors, x = [], [], None
    cherns, chern_errors, chern_x = [], [], None
    acc_boxplot_data = []
    q_75ss = []
    
    for topo_type in topo_types[0:2]:
        trace_type = trace_types[0]
        task_type = task_types[0]
        if topo_type == topo_types[0]:
            pair_num = 4
        elif topo_type == topo_types[1]:
            pair_num = 8
        elif topo_type == topo_types[2]:
            pair_num = 14
        
        infile_name1, infile_name2 = init_files(
                                    trace_type, task_type, topo_type,
                                    x_var = 'PVALUEBYTE'
        )
        
        group_fields = ['epsilon','is_correlated', 'key']
        agg_fields = ['count_chern', 'byte_chern']
        chern_x, case_num, acc_dict = retieveData(
                infile_name2, group_fields, agg_fields, 
                accuracys, errors, div=False, pair_num=pair_num, q_75ss=q_75ss
        )
        acc_boxplot_data.append(acc_dict.values())
    
    acc_legend = ['Database', 'Web', 'Hadoop']
    xlabel, ylabel = '$P_b$', 'Average accuracy'
    print 'accuracys, chern_x', len(accuracys[0]), len(chern_x)
    pl.plot(accuracys, x=chern_x, k=2, errors=q_75ss, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1.split('/outputs')[1].split('.csv')[0].replace('.', '_'), 
        xlog=True, ylog=False, acc_legend=acc_legend, legend_x=0.2,
        legend_y=0.2
    )
    print acc_boxplot_data
    
    pl.box_plot([acc_boxplot_data[0]], x=chern_x, k=2, errors=errors, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1.split('/outputs')[1].split('.csv')[0].replace('.', '_'), 
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
