import os
import numpy as np

def init_files(trace_type = ' ', task_type='CLASSIFICATION', topo_type='b4', 
                x_var = 'FLOWNUM'
    ):
    file_name1 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_trace'+trace_type+'.csv')
    file_name2 = ('../outputs/zout_'
            +topo_type.lower()+'_'+ task_type.lower() + '_' 
            + x_var.lower() + '_chern_trace'+trace_type+'.csv')
            
    f1 = open(file_name1, 'w')
    if task_type =='APPLICATION':
        f1.write(("#flows,bias_threshold,is_correlated,#case_detect\n"))
    else:
        if task_type =='CLASSIFICATION':
            f1.write(("#flows,epsilon,is_correlated,#correlated_detect,#non-uniform_detect,#all_cases\n"))
        elif task_type =='RANKING':
            f1.write(("#flows,epsilon,is_correlated,#correlated_detect\n"))
        else:
            f1.write(("#flows,bias_threshold,imr_threshold,is_correlated,#correlated_detect,#non-uniform_detect,#all_cases\n"))
    
    
    f2 = open(file_name2, 'w')
    if task_type =='CLASSIFICATION':
        f2.write('#flows,epsilon,'
                    + 'is_correlated,'
                    + 'key,count_chern,byte_chern,pred,true\n'
    )
    elif task_type =='RANKING':
        f2.write('#flows,epsilon,'
                        + 'is_correlated,'
                        + 'key,#pres,count_chern[0]\n'
        )

    elif task_type =='APPLICATION':
        f2.write('#flows,r_threshold,'
                        + 'is_correlated,'
                        + 'drop_id,key,pred,true\n'
        )
    print(file_name1, '\n', file_name2)
    f1.close()
    f2.close()

def run_single(topo_type, task_type, trace_type, iterations, 
                x_var='FLOWNUM'):
    # B4
    if topo_type == "B4":
        if task_type == 'CLASSIFICATION':
        
            flow_nums = [500] + np.arange(1000, 4600, 500)
            flow_nums = np.arange(50, 550, 50)
            epsilons = [0.01] #np.arange(0.01, 0.12, 0.02)
        if task_type == "RANKING":
            flow_nums = np.arange(20, 110, 20)
            epsilons = np.arange(0.01, 0.12, 0.02)
        if task_type == "APPLICATION":
            flow_nums = [4500]
            epsilons = [0.01]
    
    # Tree
    if topo_type == "TREE":
        if task_type == 'CLASSIFICATION':
            flow_nums = np.arange(50, 550, 50) #np.arange(200, 2100, 300)
            epsilons = [0.01] # np.arange(0.01, 0.4, 0.04)
        if task_type == "RANKING":
            flow_nums = np.arange(100, 610, 50)
            epsilons = np.arange(0.01, 0.4, 0.04)
        if task_type == "APPLICATION":
            flow_nums = [2100]
            epsilons = [0.01]
    
    # Jupiter
    if topo_type == "JUPITER":
        if task_type == 'CLASSIFICATION':
            flow_nums = np.arange(5000, 36000, 2500) # 5000, 30000
            epsilons = [0.01] #np.arange(0.01, 0.22, 0.04)
        if task_type == "RANKING":
            flow_nums = np.arange(400, 1700, 200)
        if task_type == "APPLICATION":
            flow_nums = [2000]
            epsilons = [0.01]
    
    if x_var == 'BIAS':        
        r_thresholds = [0.05, 0.1, 0.2, 0.3, 0.4]
        imr_thresholds = [0.1]
    else:
        r_thresholds = [0.3]
        imr_thresholds = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    drop_ids = [0]
    
    if x_var == 'FLOWNUM' or x_var == 'PVALUE':
        r_thresholds = [0.3]
        imr_thresholds = [0.1]
    
    if x_var == 'PVALUE':
        flow_nums = flow_nums[len(flow_nums)-1:]
    if x_var == 'FLOWNUM':
        epsilons = epsilons[0:1]
    
    print '@flow_nums', flow_nums
    print '@epsilons', epsilons
    print '@r_thresholds', r_thresholds
    print '@imr_thresholds', imr_thresholds
    
    init_files(trace_type, task_type, topo_type, x_var=x_var)
    for iter in range(iterations):
        for flow_num in flow_nums:
            for epsilon in epsilons:
                for r_threshold in r_thresholds:
                    for imr_threshold in imr_thresholds:
                        is_correlated, drop_id = 1, 0
                        print '\n@CORRELATED '
                        command = ('python mesh_topo.py ' 
                                            + topo_type + ' ' 
                                            + str(flow_num) + ' '
                                            + str(is_correlated) + ' '
                                            + trace_type + ' '
                                            + task_type + ' '
                                            + x_var + ' '
                                            + str(epsilon) + ' '
                                            + str(r_threshold) + ' '
                                            + str(drop_id) + ' '
                                            + str(imr_threshold)
                        )
                        os.system(command)
                        
                        if task_type == "CLASSIFICATION":
                            print('\n@NOT CORRELATED')
                            is_correlated, drop_id = 0, 0
                            command = ('python mesh_topo.py ' 
                                        + topo_type + ' ' 
                                        + str(flow_num) + ' '
                                        + str(is_correlated) + ' '
                                        + trace_type + ' '
                                        + task_type + ' '
                                        + x_var + ' '
                                        + str(epsilon) + ' '
                                        + str(r_threshold) + ' '
                                        + str(drop_id) + ' '
                                        + str(imr_threshold)
                                        
                            )
                            os.system(command)
                        
                        if task_type == "APPLICATION":
                            for drop_id in drop_ids:
                                print('NOT CORRELATED')
                                is_correlated = 0
                                command = ('python mesh_topo.py ' 
                                            + topo_type + ' ' 
                                            + str(flow_num) + ' '
                                            + str(is_correlated) + ' '
                                            + trace_type + ' '
                                            + task_type + ' '
                                            + x_var + ' '
                                            + str(epsilon) + ' '
                                            + str(r_threshold) + ' '
                                            + str(drop_id) + ' '
                                            + str(imr_threshold)
                                            
                                )
                                os.system(command)
         
if __name__ == '__main__':
    
    task_types = ['CLASSIFICATION', 'RANKING', 'APPLICATION']
    trace_types = ['A', 'B', 'C', 'e1', 'e5', 'e10', 'e50', 'e100', 'ABC']
    topo_types = ['B4', 'TREE', 'JUPITER']
    x_vars = ['FLOWNUM', 'PVALUE', 'BIAS', 'IMR']
    
    iterations = 1
    topo_type = topo_types[1]
    x_var = x_vars[0]
    
    for task_type in task_types[1:2]:
        for trace_type in trace_types[0:3]:
            run_single(topo_type, task_type, trace_type, iterations, 
                x_var=x_var)
