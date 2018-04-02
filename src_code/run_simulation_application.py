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
        f1.write(("#flows,iteration,r_threshold,imr_threshold,is_correlated,#case_detect,len(class_dict)\n"))
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
        f2.write('#flows,iteration,time,r_threshold,imr_threshold,'
                        + 'is_correlated,'
                        + 'drop_id,key,pred,true,imr0,imr1\n'
        )
    print(file_name1, '\n', file_name2)
    f1.close()
    f2.close()

def run_single(topo_type, task_type, trace_type, iter_start=0, iter_end=10, 
                x_var='FLOWNUM'):
    # B4
    if topo_type == "B4":
        if task_type == 'CLASSIFICATION':
        
            flow_nums = [500] + np.arange(1000, 4600, 500)
            flow_nums = np.arange(50, 410, 50)#np.arange(50, 410, 25) #np.arange(675, 860, 50)#np.arange(225, 660, 50)#np.arange(50, 210, 25)

            flow_nums = [350]
            epsilons = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.4] 
 

        if task_type == "RANKING":
            flow_nums = np.arange(10, 110, 10)
            epsilons = np.arange(0.01, 0.12, 0.02)
        if task_type == "APPLICATION":
            flow_nums = [4500]
            epsilons = [0.01]
    
    # Tree
    if topo_type == "TREE":
        if task_type == 'CLASSIFICATION':
            flow_nums = np.arange(50, 410, 50)#np.arange(50, 410, 25)#np.arange(225, 660, 50)#np.arange(50, 210, 25)#np.arange(50, 250, 50) #np.arange(200, 2100, 300)

            epsilons = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.2, 0.4]

        if task_type == "RANKING":
            flow_nums = np.arange(10, 110, 10) #np.arange(100, 610, 50)
            epsilons = [0.005] 
        if task_type == "APPLICATION":
            flow_nums = [800]
            epsilons = [0.01]
    
    # Jupiter
    if topo_type == "JUPITER":
        if task_type == 'CLASSIFICATION':
            flow_nums = np.arange(800, 1260, 50) #np.arange(50, 260, 25)#np.arange(5000, 36000, 2500) # 5000, 30000
            flow_nums = np.arange(300, 310, 100) 
            epsilons = [0.0001, 0.001, 0.01, 0.1, 0.2, 0.4] #np.arange(0.01, 0.22, 0.04)
        if task_type == "RANKING":
            flow_nums = [100] #np.arange(20, 110, 20) #np.arange(400, 1700, 200)
            epsilons = [0.005] #np.arange(0.01, 0.22, 0.04)
        if task_type == "APPLICATION":
            flow_nums = [800]
            epsilons = [0.01]
    
    if x_var == 'BIAS' or 'RTHRESHOLD' in x_var:        
        r_thresholds = np.arange(0.2, 0.4, 0.1) #[0.05, 0.1, 0.2, 0.3, 0.4]
        #r_thresholds = [0.002, 0.004, 0.006, 0.008, 0.01, 0.012]

        imr_thresholds = [0.1]
    else:
        r_thresholds = [0.25]
        imr_thresholds = np.arange(0.025, 0.26, 0.025)#[0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
    drop_ids = [0]
    
    if 'FLOWNUM' in x_var or 'PVALUE' in x_var:
        r_thresholds = [0.01]
        imr_thresholds = [0.1]
    
    if 'PVALUE' in x_var or 'RTHRESHOLD' in x_var:
        flow_nums = [400] #flow_nums[len(flow_nums)-1:]
        if topo_type == "JUPITER":
            flow_nums = [19000]
    if 'FLOWNUM' in x_var or 'RTHRESHOLD' in x_var:
        epsilons = [0.001]
    
    print '@flow_nums', flow_nums
    print '@epsilons', epsilons
    print '@r_thresholds', r_thresholds
    print '@imr_thresholds', imr_thresholds

    
    for iteration in range(iter_start, iter_end):
        if iteration == 0:
            init_files(trace_type, task_type, topo_type, x_var=x_var, p=0.01)
        for flow_num in flow_nums:
            for epsilon in epsilons:
                for r_threshold in r_thresholds:
                    for imr_threshold in imr_thresholds:
                        """is_correlated, drop_id = 1, 0
                        #r_threshold = 0.1
                        drop_id = 0
                        if task_type == 'RANKING':
                            drop_id = 0
                        print '\n@CORRELATED ', '@r_thresholds, @iteration', r_threshold, iteration
                        command = ('python mesh_topo_application.py ' 
                                            + topo_type + ' ' 
                                            + str(flow_num) + ' '
                                            + str(is_correlated) + ' '
                                            + trace_type + ' '
                                            + task_type + ' '
                                            + x_var + ' '
                                            + str(epsilon) + ' '
                                            + str(r_threshold) + ' '
                                            + str(drop_id) + ' '
                                            + str(imr_threshold) + ' '
                                            + str(iteration)
                        )
                        os.system(command)"""
                        
                        if task_type == "APPLICATION":
                            print '\n@ NOT CORRELATED ', '@r_thresholds, @iteration', r_threshold, iteration
                            #for drop_id in drop_ids:
                            drop_id = 1
                            is_correlated = 0
                            command = ('python mesh_topo_application.py ' 
                                        + topo_type + ' ' 
                                        + str(flow_num) + ' '
                                        + str(is_correlated) + ' '
                                        + trace_type + ' '
                                        + task_type + ' '
                                        + x_var + ' '
                                        + str(epsilon) + ' '
                                        + str(r_threshold) + ' '
                                        + str(drop_id) + ' '
                                        + str(imr_threshold) + ' '
                                        + str(iteration)
                                        
                            )
                            os.system(command)
                        
                        """if task_type == "APPLICATION":
                            print '\n@ NOT CORRELATED NO DROP', '@r_thresholds, @iteration', r_threshold, iteration
                            #for drop_id in drop_ids:
                            drop_id = -1
                            is_correlated = 0
                            command = ('python mesh_topo_application.py ' 
                                        + topo_type + ' ' 
                                        + str(flow_num) + ' '
                                        + str(is_correlated) + ' '
                                        + trace_type + ' '
                                        + task_type + ' '
                                        + x_var + ' '
                                        + str(epsilon) + ' '
                                        + str(r_threshold) + ' '
                                        + str(drop_id) + ' '
                                        + str(imr_threshold) + ' '
                                        + str(iteration)
                                        
                            )
                            os.system(command)"""
         
if __name__ == '__main__':
    
    task_types = ['CLASSIFICATION', 'RANKING', 'APPLICATION']
    trace_types = ['A', 'B', 'C', 'e1', 'e5', 'e10', 'e50', 'e100', 'ABC']
    topo_types = ['B4', 'TREE', 'JUPITER']
    x_vars = ['CHERNFLOWNUM', 'TTESTFLOWNUM', 'CHERNTTFLOWNUM', 'TTESTRTHRESHOLD', 'TTESTPVALUE', 'TTESTPVALUEBYTE', 'BIAS', 'IMR']
    x_vars = ['TTESTFLOWNUM',  'TTESTPVALUE', 'TTESTPVALUEBYTE', 'TTESTRTHRESHOLD', 'BIAS', 'IMR']
    x_vars1 = ['CHERNFLOWNUM','CHERNPVALUE', 'CHERNPVALUEBYTE', 'CHERNRTHRESHOLD']

    topo_type = topo_types[2]
    x_var = 'CHERNRTHRESHOLD' #check x_var caution init_file
    iter_start, iter_end = 0, 1
    for task_type in task_types[2:3]:
        for trace_type in trace_types[-1:]:
            run_single(topo_type, task_type, trace_type, iter_start=iter_start, iter_end=iter_end, 
                x_var=x_var)
