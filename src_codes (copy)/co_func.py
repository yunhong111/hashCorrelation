from collections import OrderedDict
import bound as bd
import numpy as np

def append_path(hash_str, pre_hop, cur_hop, paths):
    if hash_str not in paths:
        paths[hash_str] = OrderedDict({})
    if cur_hop not in paths[hash_str]:
        paths[hash_str][(pre_hop, cur_hop)] = 1

def min_bound(next_counts):
    
    n = len(next_counts)
    min_bound = 1.1
    min_pos = -1
    sum_HHes = np.float64(sum(next_counts))
    for i in range(n):
        o_fi = float(next_counts[i])/sum(next_counts)
        ratio = 1.0/len(next_counts)
        if o_fi <= ratio:
            flow_fractions = [float(1.0)/sum_HHes]*sum_HHes
            theta, chern_bound = bd.chernoff_min(
                    flow_fractions, o_fi, ratio=ratio
            )
            if chern_bound < min_bound:
                min_bound = chern_bound
                min_pos = i
            print(
                'chern_bound, o_fi, ratio, min_bound', 
                chern_bound, o_fi, ratio, min_bound
            )
    return min_bound
