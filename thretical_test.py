import numpy as np
import bound as bd

def crc_test():
    

HHes = [1]*10 + [0]*10
print HHes
o_f = 0.5
theta, bound = bd.chernoff_min(HHes, o_f, ratio = 0.5)
print(theta, bound)
