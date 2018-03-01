import pandas as pd
import numpy as np
import math
from scipy import optimize

def hoefding_HHes(HHes, x, alpha):
    sum_HHes = np.float64(sum(HHes))
    flow_fractions = [np.float64(f)/np.float64(sum_HHes) for f in HHes]
    return hoefding(flow_fractions, x, alpha)
    
def hoefding(flow_fractions, x, alpha):
    x = x - alpha
    f_sum = 0
    for fi in flow_fractions:
        f_sum += math.pow(fi,2.0)
    return math.exp(-math.pow(x,2.0)/f_sum)

def chernoff_fun(theta):
    global flow_fractions, x, alpha
    comp1 = math.exp(-theta*x)
    e_proc = 1.0
    for fi in flow_fractions:
        try:
            ans = math.exp(theta*fi)
        except OverflowError:
            ans = float('inf')
            
        e_proc *= (ans*alpha+1-alpha)
    return comp1*e_proc    
    
def chernoff_min(HHes, o_f, ratio = 0.5):
    global flow_fractions, x, alpha
    x = o_f
    alpha = ratio
    #sum_HHes = np.float64(sum(HHes))
    flow_fractions = HHes #[np.float64(f)/sum_HHes for f in HHes]
    theta = optimize.fmin(chernoff_fun, 1, disp=False)
    ch_bound = chernoff_fun(theta[0])
    return theta[0], ch_bound

def chernoff_min_theta(HHes, o_f, ratio = 0.5):
    global flow_fractions, x, alpha
    if len(HHes) == 0 or o_f == 1:
        return 0, 0
    x = o_f
    alpha = ratio
    flow_fractions = HHes
    f1 = flow_fractions[0]
    theta = ((np.float64(1.0) / np.float64(f1))
                * math.log(o_f * (1.0 - alpha) 
                            / (alpha * (1 - o_f)), math.exp(1)
                        )
    )
    
    ch_bound = chernoff_fun(theta)
    return theta, ch_bound

