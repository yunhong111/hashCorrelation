import math
from scipy.stats import entropy

def getEntropy(data):
    """
    Compute entropy
    """
    
    data_sum = sum(data)
    print('data_sum', data_sum)
    if data_sum == 0:
        return 0
    p = [x/data_sum for x in data]
    return entropy(p)

print(getEntropy([1.0/4, 1.0/4, 1.0/4, 1.0/4]))
