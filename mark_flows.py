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
            #if len(routing_table[s_d][d]) > 1:
                if d not in mark_group:
                    mark_group[d] = []
                mark_group[d] += routing_table[s_d][d]
                mark_group[d] = list(set(mark_group[d]))
    
    for key in mark_group:
        mark_group[key] += [key]
    return mark_group
    
def marknum(hash_str, count_dict, mark_dict, threshold, mark_group):
    """
    Determine how many packets to mark such that 
    we can get a complete path
    """
    if hash_str not in count_dict:
        count_dict[hash_str] = 2
        mark_dict[hash_str] = {}
        
    switch_id = mark(mark_group, count_dict[hash_str])
    count_dict[hash_str] += 1
    
    if switch_id not in mark_dict[hash_str]:
        mark_dict[hash_str][switch_id] = 0
    mark_dict[hash_str][switch_id] += 1
    #if count_dict[(hash_str, switch_id)] > threshold:
        #return 'None'
    
    return switch_id
    
def mark(mark_group, count):
    """
    Return a switch ID it may be tranversing
    Currently, all switch IDs are in considering
    """
    
    n = len(mark_group)
    pos = random.randint(0, n-1) #count % n #
    return mark_group[pos]

def mark_random(p=0.1):
    r = random.random()
    if r < p:
        return "1"
    return "0"
    
    

