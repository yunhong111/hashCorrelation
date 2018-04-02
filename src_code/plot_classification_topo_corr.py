
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plot_lib as pl
from sklearn.metrics import accuracy_score
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
        names=(['#flows', 'epsilon', 'is_correlated', 
                'key', 'count_chern', 'byte_chern', 'pred']
        )
        return pd.read_csv(file_name) #, skiprows=[0], names=names
    else:
        names=['#flows', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        if is_epsilon:
            names=['#flows', 'epsilon', 'is_correlated', 'key'] + ['a' + str(i) for i in range(ACAP)]
        return pd.read_csv(file_name) #, skiprows=[0], names=names

def retieveData(infile_name1, group_fields, agg_fields, 
                accuracys, errors, times, div=False, 
                task_type="CLASSIFICATION", file_type=0, 
                iteration=10, pair_num=4, key_field='#flows', q_75ss=[], xss=[]
    ):
    print infile_name1
    df1 = read_csv(infile_name1, file_type)
    df1 = df1.replace([2, '2.0', 2.0, '2'], 1)
    df1 = df1[df1['is_correlated'] == 1] # group*2
    #print df1
    #df1['true'] = df1['is_correlated'].replace([0], -1)
    df1['colFromIndex'] = df1.index
    df1 = df1.sort(columns=[key_field, 'iteration'])
    df1_part1 = df1[df1['is_correlated'] == 0]
    df1_part2 = df1[df1['is_correlated'] == 1]
    
    #df1 = df1[df1['#flows']%50 == 0] 
    
    print df1.groupby(['#flows']).count()
    time_df = (df1
            .groupby('#flows')
            .agg({'time':['mean']})
    )

    times.append(time_df['time']['mean'])
    print 'times', times
    df1 = df1.reset_index()
    df1_part1 = df1_part1.reset_index()
    df1_part2 = df1_part2.reset_index()

    pvalue_num = df1[key_field].unique().shape[0]
    group_num = pair_num
    acc_dict = OrderedDict({})
    for i in range(iteration*pvalue_num):
        s_index = i*group_num
        e_index = (i+1)*group_num - 1
        print 'index', s_index, e_index, len(df1), group_num, iteration*pvalue_num

        #if e_index <= len(df1)+1:
        if df1[key_field].loc[s_index] != df1[key_field].loc[e_index]:
            print df1.loc[s_index], df1.loc[e_index]
            eeee
        key = df1[key_field].loc[e_index]
        print 'key', key

        y_pred = df1['pred'].loc[s_index:e_index+1]
        #y_pred = y_pred.append(df1_part2['pred'].loc[s_index:e_index])
        y_true = df1['true'].loc[s_index:e_index+1]
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
    xss.append(list(df1[key_field].unique()))
    
    return df1[key_field].unique(), pvalue_num, acc_dict
    
def accuracyPlot(topo_types, task_types, c, pair_seq=0):
    
    accuracys, errors, times, x = [], [], [], None
    cherns, chern_errors, chern_x = [], [], None
    acc_boxplot_data = []
    q_75ss, xss = [], []
    
    for topo_type in topo_types[0:1]:
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
                                    x_var = 'XFLOWNUM'
        )
        
        infile_name3, infile_name4 = init_files(
                                    trace_type, task_type, topo_type,
                                    x_var = 'TTESTFLOWNUM'
        )
        
        infile_name5, infile_name6 = init_files(
                                    trace_type, task_type, topo_type,
                                    x_var = 'CHERNTTFLOWNUM'
        )
        
        group_fields = ['#flows','is_correlated', 'key']
        agg_fields = ['count_chern', 'byte_chern']
        chern_x, case_num, acc_dict = retieveData(
                infile_name2, group_fields, agg_fields, 
                accuracys, errors, times, div=False, pair_num=pair_num, q_75ss=q_75ss,
                xss=xss
        )
        chern_x, case_num, acc_dict = retieveData(
                infile_name4, group_fields, agg_fields, 
                accuracys, errors, times, div=False, pair_num=pair_num, q_75ss=q_75ss,
                xss=xss
        )
        """chern_x, case_num, acc_dict = retieveData(
                infile_name6, group_fields, agg_fields, 
                accuracys, errors, times, div=False, pair_num=pair_num, q_75ss=q_75ss
        )"""
        acc_boxplot_data.append(acc_dict.values())
    
    acc_legend = ['Chernoff', 'T-test','Chernoff-T-test']
    acc_legend = ['Tree-Chernoff', 'Tree-T-test'] #'B4-Chernoff', 'B4-T-test',
    xlabel, ylabel = 'The number of flows', 'Average accuracy'
    len_x = min([len(acc) for acc in accuracys])
    #accuracys = [acc[:len_x] for acc in accuracys]
    #chern_x = chern_x[:len_x]
    print accuracys, xss
    print len(chern_x), len(accuracys[0])
    pl.plot(accuracys, x=xss, k=2, errors=q_75ss, 
        xlabel=xlabel, ylabel=ylabel, title=infile_name1.split('/outputs')[1].split('.csv')[0].replace('.', '_')+'_corr', 
        xlog=False, ylog=False, acc_legend=acc_legend[:len(accuracys)],
        legend_y=0.23, legend_x=0.2
    )
    
    pl.plot(times, x=xss, k=2, errors=q_75ss, 
        xlabel=xlabel, ylabel='Execute time (seconds)', title=infile_name1.split('/outputs')[1].split('.csv')[0].replace('.', '_') + '_corr_time', 
        xlog=False, ylog=False, acc_legend=acc_legend,
        legend_y=0.25, legend_x=0.15
    )
    
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
    accuracyPlot(topo_types, task_types, trace_types[0:1], pair_seq=pair_seq)
    plt.show()
