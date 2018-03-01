from scipy import stats
import pandas as pd
import numpy as np

def independentCluster(table, p_t):
    """
    * Split the table to several tables
    """
    
    apps = list(table.columns.values)
    n0 = len(apps)
    nn = 0
    count = 0
    while(nn != n0):
        
        n0 = len(apps)
        apps_compliment = []
        
        while len(apps) != 0:
            a1 = [apps[0]] if isinstance(apps[0], str) else apps[0]
            max_p, max_a, max_ai = 0, [], None
            apps = apps[1:]

            for i, a2 in enumerate(apps):
                if isinstance(a2, str):
                    a2 = [a2] 
                table1 = table[a1+a2]
                ret = stats.chi2_contingency(observed=table1)
                p = ret[1]
                if max_p < p:
                    max_p, max_a, max_ai = p, a2, i
                    
            tmp = a1
            if max_p > p_t:
                tmp += max_a
                if max_ai != None:
                    print max_a
                    apps.remove(apps[max_ai])

            apps_compliment.append(tmp)
            count += 1
            #if count == 5:
                #eee
        apps = apps_compliment        
        nn = len(apps_compliment)

    app_imrs = []
    for app in apps:
        inner_max, inner_min, inner_p = 0, 0, 0
        
        for a in app:
            inner_max += table[a].max()
            inner_min += table[a].min()
        inner_imr = float(inner_max-inner_min)/inner_max
        
        if len(app) > 1:
            table1 = table[app]
            ret = stats.chi2_contingency(observed=table1)
            inner_p = ret[1]
        else:
            inner_p = 1.0
        app_imrs.append((app, inner_p, inner_imr))
    print app_imrs
    return app_imrs

"""d = {'a1': [1, 2, 5, 6], 'a2': [3, 4, 7, 8], 'a3': [1, 2, 5, 6], 'a4': [3, 4, 7, 8]}
d = ({'a1': [9,3,31,38,24,4,27,6],
        'a2': [307,345,1020,972,1020,349,1034,347],
        'a3': [10,10,35,39,43,15,48,9],
        'a4': [170,180,556,505,566,202,524,187],
        'a5': [19,24,66,56,70,17,62,20]})
        
d = ({'a1': [19,17,18,15,24,21,14,14],
        'a2': [307,345,1020,972,1020,349,1034,347],
        'a3': [30,33,12,29,35,21,26,23],
        'a4': [350,365,364,354,377,381,379,320],
        'a5': [50,45,35,34,50,56,38,26]
        })
table = pd.DataFrame(data=d)

independentCluster(table, 0.01)"""
