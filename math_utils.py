import numpy as np 

def get_l1_norm(p1, p2): 
    return float(abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])) 

def get_expected_value(matrix, coord): 
    return 0.5