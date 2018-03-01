import random
"""
Mark packets in a flow
Options:
    Mark every packet
    Mark some packet (This is resonable)
"""
def mark_group_dest(routing_table):
    """
    How to mark packets according to destination
    only mark thoes with multi-path
    """
    mark_group = {}
    for s_d in routing_table:
        for d in routing_table[s_d]:
            if len(routing_table[s_d][d]) > 1:
                if d not in mark_group:
                    mark_group[d] = []
                mark_group[d] += routing_table[s_d][d]
                mark_group[d] = list(set(mark_group[d]))
    return mark_group
    
def marknum(hash_str, count_dict, threshold, mark_group):
    """
    Determine how many packets to mark such that 
    we can get a complete path
    """
    
    if hash_str not in count_dict:
        count_dict[hash_str] = 0
    count_dict[hash_str] += 1
    if count_dict[hash_str] > threshold:
        return 'None'
    switch_id = mark(mark_group)
    return switch_id
    
def mark(mark_group):
    """
    Return a switch ID it may be tranversing
    Currently, all switch IDs are in considering
    """
    
    n = len(mark_group)
    pos = random.randint(0, n-1)
    return mark_group[pos]
    
    

