from scipy import stats
import math
import numpy as np

def t_test(next_counts, popmean):
    next_counts = sorted(next_counts, reverse=True)
    sum_count = sum(next_counts)
    if sum_count == 0:
        return 0, 1
        
    n = len(next_counts)
    values = [0 + 1.0/(n-1)*i for i in range(n)]
    amean = sum([next_counts[i]*values[i] for i in range(n)]) / sum_count
    sdsq = (sum([(values[i]-amean)**2*next_counts[i] for i in range(n)]) 
            / float(sum_count - 1)
    )
    se = math.sqrt(sdsq/sum_count)
    if se == 0:
        return 1, 0
    t = (amean-popmean)/se
    p = stats.t.sf(np.abs(t), sum_count-1)*2
    return t, p

def t_test_byte(next_counts, popmean):
    sum_count = sum([x for sub in next_counts for x in sub])
    next_counts = sorted(next_counts, key=lambda x: sum(x), reverse=True)
    
    if sum_count == 0:
        return 0, 1
        
    n = len(next_counts)
    m = sum([len(x) for x in next_counts])
    values = [0 + 1.0/(n-1)*i for i in range(n)]
    data = [x*values[i]*m/sum_count for i in range(n) for x in next_counts[i]]
    #print('        %%t_test_byte:mean(data)', np.mean(data))
    return stats.ttest_1samp(data, popmean)
    
#a, b = (t_test_byte([[0.0066468891851984742, 0.0074553244730892979, 0.0087542919064033681, 0.0088453326217803451, 0.010474469385258239, 0.0090006100433513096, 0.0079711511505359545, 0.0091887031175112363, 0.0095306607248750626, 0.0078344962867159286, 0.022637962907307969, 0.0084130895194564886, 0.0085104535806360473, 0.012116844265840658, 0.0096192334636940862, 0.14053929121621819, 0.0071565575253126441, 0.056917702465088274, 0.0077402481950810398, 0.13688487305244942, 0.0084267797781764943, 0.010421397665364471, 0.026626472404089968, 0.0089291257284821873, 0.0084025920651248955, 0.016532679864097493, 0.0075496574208466383, 0.007153783795335788], [0.010511961359157475, 0.0053271718575360356, 0.01111459248981555, 0.0065092484557299239, 0.024021991473858195, 0.010242920788712003, 0.0085706251606652087, 0.14184575309147626, 0.025855280601850026, 0.0086695863178537901, 0.0074006333812295126, 0.0073339604768394295, 0.0097626560369458212, 0.0051791222660265129, 0.0074410556242522144, 0.010273603187600008, 0.0069215623329316996, 0.0057558068828626827, 0.0073211372278261973, 0.010243283265472429, 0.0099838000016370144, 0.0088958096329919342, 0.0099049666293675506, 0.0095665278618257132, 0.0056988102749311173, 0.0045809031790600375, 0.007783058219122463, 0.009911141056733035, 0.0068587903109288461, 0.0062335667474391777]], 0.5))

