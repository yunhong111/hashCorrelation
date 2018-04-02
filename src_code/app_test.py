from random import randint
from collections import Counter
import numpy as np
import pandas as pd
import independent_set as iset
import application as appl
import os
import numpy as np
import co_func as cf

def init_files(trace_type = ' ', task_type='CLASSIFICATION', topo_type='b4', 
                x_var = 'FLOWNUM', p=0.01
    ):
    file_name1, file_name2 = cf.init_files(trace_type=trace_type, 
                task_type=task_type, topo_type=topo_type, 
                x_var=x_var, p=p)
                
    f1 = open(file_name1, 'w')
    if task_type =='APPLICATION':
        f1.write(("#flows,iteration,r_threshold,imr_threshold,p_t,topk,is_correlated,#case_detect,len(class_dict)\n"))
    else:
        if task_type =='CLASSIFICATION':
            f1.write(("#flows,iteration,epsilon,r_threshold,is_correlated,#correlated_detect,#non-uniform_detect,#all_cases\n"))
        elif task_type =='RANKING':
            f1.write(("#flows,iteration,epsilon,r_threshold,is_correlated,#correlated_detect\n"))
        else:
            f1.write(("#flows,iteration,r_threshold,imr_threshold,is_correlated,#correlated_detect,#non-uniform_detect,#all_cases\n"))
    
    
    f2 = open(file_name2, 'w')
    if task_type =='CLASSIFICATION':
        f2.write('#flows,iteration,time,epsilon,r_threshold,'
                    + 'is_correlated,'
                    + 'key,count_chern,byte_chern,pred,true\n'
    )
    elif task_type =='RANKING':
        f2.write('#flows,iteration,time,epsilon,r_threshold,'
                        + 'is_correlated,'
                        + 'key,#pres,o_f,count_chern[0]\n'
        )
            
    elif task_type =='APPLICATION':
        f2.write('#flows,iteration,time,r_threshold,imr_threshold,p_t,topk,'
                        + 'is_correlated,'
                        + 'drop_id,key,pred,true,imr0,imr1,imr2\n'
        )
    print(file_name1, '\n', file_name2)
    f1.close()
    f2.close()

def app_classification(app_flows1, app_flows2, app_flows3, x_var='', key='', iteration=0, is_correlated=0, imr_threshold=0.1, select_len=1, app_exc_time=0, r_threshold=0.1, x_type=1, p_t=0.01, topk=1):
    
    app1 = sorted(Counter([randint(0,8) for p in range(0,app_flows1)]).values())
    app2 = sorted(Counter([randint(0,8) for p in range(0,app_flows2)]).values())
    app3 = sorted(Counter([randint(0,8) for p in range(0,app_flows3)]).values())
    #print 'r_threshold', r_threshold
    drop_id = 3

    if is_correlated == 0 and x_type == 2:
        drop_link_id = randint(0, 8)
        app_x = app3
        app_x[drop_link_id] = int(app_x[drop_link_id]*(1-r_threshold))
        app_x = sorted(app_x)
        app3 = app_x
    elif is_correlated == 1 and x_type == 1:
        for i in range(4):
            app1[i], app2[i], app3[i] = 0.1, 0.1, 0.1
            
    topk = topk
    app_top1 = app1[0:topk] + app1[-topk:]
    app_top2 = app2[0:topk] + app2[-topk:]
    app_top3 = app3[0:topk] + app3[-topk:]
    
    app_link_table = []
    app_link_table.append(app_top1)
    app_link_table.append(app_top2)
    app_link_table.append(app_top3)

    app_link_table = np.transpose(np.array(app_link_table))
    top_apps = [1,2,3]
    app_df = pd.DataFrame(
        app_link_table, columns=['a' + str(x) for x in top_apps])

    app_imrs = iset.independentCluster(app_df, p_t)

    class_dict = {}
    appl.appClassification(
        len(app_imrs), app_imrs[0][2], 
        key=key, imr_threshold=0.1, class_dict=class_dict)

    imrs = [x[2] for x in app_imrs]

    file_name1, file_name2 = cf.init_files(trace_type='ABC', 
                    task_type='APPLICATION', topo_type='JUPITER', 
                    x_var=x_var, p=0.01)
                
    f1 = open(file_name1, 'a')
    f2 = open(file_name2, 'a')
        
    if task_type == "APPLICATION":    
        # Ranking result
        true_num = 0
        for key in class_dict:
            true_class = 0
            true_class = x_type
            f2.write(
                    str(select_len) + ','
                    + str(iteration) + ','
                    + str(app_exc_time) + ','
                    + str(r_threshold) + ','
                    + str(imr_threshold) + ','
                    + str(p_t) + ','
                    + str(topk) + ','
                    + str(int(is_correlated)) + ','
                    + str(int(drop_id)) + ','
                    + key + ','
                    + str(class_dict[key]) + ','
                    + str(true_class) + ','
                    + ','.join([str(x) for x in imrs]) + '\n'
            )

            if true_class == class_dict[key]:
                true_num += 1

        f1.write(
            ','.join([str(x) for x in 
            [select_len, iteration, r_threshold, imr_threshold, p_t, topk, int(is_correlated), 
            true_num, len(class_dict)]]
            ) 
            + '\n'
        )
        
app_flows10 = sum([1054, 1073, 1074, 1081, 1109, 1111, 1117, 1139]) 
app_flows20 = sum([97, 109, 124, 131, 136, 138, 144, 155]) - 34
app_flows30 = sum([255, 257, 269, 270, 274, 279, 280, 287])

iter_start, iter_end = 10, 20
x_vars = ['CHERNFLOWNUM', 'CHERNRTHRESHOLD', 'CHERNPAVLUE', 'TOPKONE', 'TOPKONEFIVE', 'TOPKTWO']
trace_type, task_type, topo_type, x_var = 'ABC', 'APPLICATION', 'JUPITER', 'TOPKTWO'
imr_threshold = 0.1
if x_var == 'CHERNFLOWNUM':
    flow_nums =np.arange(0.5, 4.5, 0.5)
    r_thresholds = [0.2]
    topks = [2]
    p_ts = [0.1]
if x_var == 'CHERNRTHRESHOLD':
    flow_nums = [4]
    r_thresholds = np.arange(0.125, 0.32, 0.025)
    topks = [2]
    p_ts = [0.1]

if x_var == 'CHERNPAVLUE':
    flow_nums = [4]
    r_thresholds = [0.2]
    topks = [2]
    p_ts = [0.0001, 0.001, 0.01, 0.1, 0.2, 0.4]

if 'TOPK' in x_var:
    flow_nums = [4]
    r_thresholds = [0.2]
    topks = [1,2,3,4]
    p_ts = [0.1]
    if x_var == 'TOPKONE':
        r_thresholds = [0.1]
    if x_var == 'TOPKONEFIVE':
        r_thresholds = [0.15]
print 'flow_nums, r_thresholds,topks, p_ts', flow_nums, r_thresholds,topks, p_ts
for iteration in range(iter_start, iter_end):
    print 'iteration', iteration
    if iteration == 0:
        init_files(trace_type, task_type, topo_type, x_var=x_var, p=0.01)
    for r_threshold in r_thresholds:
        for p_t in p_ts:
            for topk in topks: #[1,2,3,4]: [4]:#
                for flow_multi in flow_nums:#np.arange(0.5, 4, 0.5):
                    app_flows1 = int(app_flows10*flow_multi)
                    app_flows2 = int(app_flows20*flow_multi)
                    app_flows3 = int(app_flows30*flow_multi)
                    print app_flows2
                    select_len = app_flows2
                    
                    for key in np.arange(0, 16):
                        print 'key', key
                        app_classification(app_flows1, app_flows2, app_flows3, x_var=x_var, key=str(key), iteration=iteration, is_correlated=0, imr_threshold=imr_threshold, select_len=select_len, r_threshold=r_threshold, x_type=2, p_t=p_t, topk=topk)
                        app_classification(app_flows1, app_flows2, app_flows3, x_var=x_var, key=str(key), iteration=iteration, is_correlated=1, imr_threshold=imr_threshold, select_len=select_len, r_threshold=r_threshold, x_type=1, p_t=p_t, topk=topk)
                        app_classification(app_flows1, app_flows2, app_flows3, x_var=x_var, key=str(key), iteration=iteration, is_correlated=0, imr_threshold=imr_threshold, select_len=select_len, r_threshold=r_threshold, x_type=0, p_t=p_t, topk=topk)


