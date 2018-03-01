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
    f1.write(("#flows,epsilon,is_correlated,#correlated_detect,#non-uniform_detect,#all_cases\n"))
    
    f2 = open(file_name2, 'w')
    if task_type=='CLASSIFICATION':
        f2.write('#flows,epsilon,'
                    + 'is_correlated,'
                    + 'key,count_chern,byte_chern,class\n'
    )
    elif task_type='RANKING'
        f2.write('#flows,epsilon,'
                        + 'is_correlated,'
                        + 'key,count_chern[0]\n'
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
            epsilons = np.arange(0.01, 0.12, 0.02)
        if task_type == "RANKING":
            flow_nums = np.arange(200, 1060, 50)
            epsilons = np.arange(0.01, 0.12, 0.02)
        if task_type == "APPLICATION":
            flow_nums = [4500]
    
    # Tree
    if topo_type == "TREE":
        if task_type == 'CLASSIFICATION':
            flow_nums = np.arange(200, 2100, 300)
            epsilons = np.arange(0.01, 0.4, 0.04)
        if task_type == "RANKING":
            flow_nums = np.arange(100, 610, 50)
            epsilons = np.arange(0.01, 0.4, 0.04)
        if task_type == "APPLICATION":
            flow_nums = [2100]
    
    # Jupiter
    if topo_type == "JUPITER":
        if task_type == 'CLASSIFICATION':
            flow_nums = np.arange(5000, 36000, 2500) # 5000, 30000
            epsilons = np.arange(0.01, 0.22, 0.04)
        if task_type == "RANKING":
            flow_nums = np.arange(400, 1700, 200)
        if task_type == "APPLICATION":
            flow_nums = [30000]
            
    init_files(trace_type, task_type, topo_type, x_var=x_var)
    for iter in range(iterations):
        is_correlated = 1
        for flow_num in flow_nums[len(flow_nums)-1:]:
            for epsilon in epsilons:
                command = ('python mesh_topo.py ' 
                                    + topo_type + ' ' 
                                    + str(flow_num) + ' '
                                    + str(is_correlated) + ' '
                                    + trace_type + ' '
                                    + task_type + ' '
                                    + x_var + ' '
                                    + str(epsilon)
                )
                os.system(command) 
                
            for epsilon in epsilons:    
                if task_type == "CLASSIFICATION":
                    is_correlated = 0
                    for flow_num in flow_nums[len(flow_nums)-1:]:
                        command = ('python mesh_topo.py ' 
                                    + topo_type + ' ' 
                                    + str(flow_num) + ' '
                                    + str(is_correlated) + ' '
                                    + trace_type + ' '
                                    + task_type + ' '
                                    + x_var + ' '
                                    + str(epsilon)
                        )
                os.system(command)
                
if __name__ == '__main__':
    
    task_types = ['CLASSIFICATION', 'RANKING', 'APPLICATION']
    trace_types = ['A', 'B', 'C']
    topo_types = ['B4', 'TREE', 'JUPITER']
    x_vars = ['FLOWNUM', 'PVALUE']
    
    iterations = 10
    topo_type = topo_types[2]
    x_var = x_vars[1]
    
    for task_type in task_types[0:1]:
        for trace_type in trace_types:
            run_single(topo_type, task_type, trace_type, iterations, 
                x_var=x_var)
