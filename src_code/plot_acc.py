import matplotlib.pyplot as plt
import numpy as np
flow_num = [200*i for i in range(2, 7)]
mark_first_hadoop = [0, 0, 2, 4, 4]
mark_first_cache = [0, 1, 3, 4, 4]
mark_first_web = [0,1,1,3,4]
mark_first_web_acc = [float(x)/4.0 for x in mark_first_web]
mark_first_hadoop_acc = [float(x)/4.0 for x in mark_first_hadoop]
mark_first_cache_acc = [float(x)/4.0 for x in mark_first_cache]

# Plot
fig = plt.figure(figsize=(4.3307, 3.346))
ax = plt.subplot(111)
plt.plot(flow_num, mark_first_cache_acc, 'o-', color='blue')
plt.plot(flow_num, mark_first_web_acc, '^-', color='red')
plt.plot(flow_num, mark_first_hadoop_acc, '*-', color='green')

plt.ylabel('Detection accuracy')
plt.xlabel('The number of flows')
plt.grid(True)
box = ax.get_position()
ax.set_position([box.x0+0.04, box.y0+0.15, box.width * 0.8, box.height*0.8])
plt.xticks(flow_num)
# Put a legend to the right of the current axis
acc_legend = ['Database', 'Web', 'Hadoop']
ax.legend(acc_legend, loc='center left', bbox_to_anchor=(0.6, 0.3), numpoints=1)
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
fig.savefig(
    '/home/yunhong/Research_4/trunk/figures/corr_acc' + '.png', dpi = 300)
#plt.show()

# Plot tree acc
flow_num = [100*i for i in range(1, 6)]
tree_cases_web = [0, 1, 6, 8, 8]
tree_cases_cache = [0, 1, 4, 8, 8]
tree_cases_hadoop = [0, 1, 4, 8, 8]

mark_first_web_acc = [float(x)/8.0 for x in tree_cases_web]
mark_first_cache_acc = [float(x)/8.0 for x in tree_cases_cache]
mark_first_hadoop_acc = [float(x)/8.0 for x in tree_cases_hadoop]

# Plot
fig = plt.figure(figsize=(4.3307, 3.346))
ax = plt.subplot(111)
plt.plot(flow_num, mark_first_cache_acc, 'o-', color='blue')
plt.plot(flow_num, mark_first_web_acc, '^-', color='red')
plt.plot(flow_num, mark_first_hadoop_acc, '*-', color='green')

plt.ylabel('Detection accuracy')
plt.xlabel('The number of flows')
plt.grid(True)
box = ax.get_position()
ax.set_position([box.x0+0.04, box.y0+0.15, box.width * 0.8, box.height*0.8])
plt.xticks(flow_num)
# Put a legend to the right of the current axis
acc_legend = ['Database', 'Web', 'Hadoop']
ax.legend(acc_legend, loc='center left', bbox_to_anchor=(0.6, 0.3), numpoints=1)
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
fig.savefig(
    '/home/yunhong/Research_4/trunk/figures/tree_corr_acc' + '.png', dpi = 300)

# Plot ranking for tree 20000
ranks = ([[8.56E-196,4.07E-21,1.41E-17,2.70E-16,4.61E-16,4.28E-11,5.70E-10,        7.16E-09, 6.4662618874286124e-07],
        [2.68E-197,5.68E-17,6.97E-15,1.10E-13,1.17E-10,3.72E-10,2.11E-09,2.42E-09, 0.00014743633533658324],
        [1.16E-215,1.88E-20,9.47E-19,8.18E-15,1.40E-13,8.32E-12,8.07E-10,1.12E-09, 5.5678461553995376e-09],
        [1.31E-200,9.25E-16,1.47E-15,2.46E-15,1.34E-12,3.34E-11,2.77E-09,1.48E-08, 7.8877317345062453e-06]]
)

fig = plt.figure(figsize=(4.3307, 3.346))
ax = plt.subplot(111)
plot_styles = ['o-', '^-', '*-', '+-']
colors = ['b', 'r', 'g', 'm']
k = 0
for rank in ranks:
    plt.plot(np.arange(len(rank)), rank, plot_styles[k], color=colors[k])
    k = k+1
plt.yscale('log')
plt.ylabel('p-value')
plt.xlabel('Ranking')
plt.grid(True)
box = ax.get_position()
ax.set_position([box.x0+0.06, box.y0+0.15, box.width * 0.8, box.height*0.8])

# Put a legend to the right of the current axis
acc_legend = ['corr pair-'+str(i) for i in range(4)]
ax.legend(acc_legend, loc='center left', bbox_to_anchor=(0.6, 0.3), numpoints=1)
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
fig.savefig(
    '/home/yunhong/Research_4/trunk/figures/tree_ranking' + '.png', dpi = 300)
    

# Plot ranking for tree 1500 flow	
ranks = ([[ 3.552713678800501e-15,0.00013625614917754875],	
 [2.2737367544323206e-13,0.0011431050868040661,0.0060710487499900405,0.0091164274466782567],
 [4.440892098500626e-16,0.00013625614917754875],		
 [1.1102230246251565e-16,0.00040252981812451821,0.0031104283103858535]]
)

fig = plt.figure(figsize=(4.3307, 3.346))
ax = plt.subplot(111)
plot_styles = ['o-', '^-', '*-', '+-']
colors = ['b', 'r', 'g', 'm']
k = 0
for rank in ranks:
    plt.plot(np.arange(len(rank)), rank, plot_styles[k], color=colors[k])
    k = k+1
plt.yscale('log')
plt.ylabel('p-value')
plt.xlabel('Ranking')
plt.grid(True)
box = ax.get_position()
ax.set_position([box.x0+0.06, box.y0+0.15, box.width * 0.8, box.height*0.8])

# Put a legend to the right of the current axis
acc_legend = ['corr pair-'+str(i) for i in range(4)]
ax.legend(acc_legend, loc='center left', bbox_to_anchor=(0.6, 0.3), numpoints=1)
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
fig.savefig(
    '/home/yunhong/Research_4/trunk/figures/tree_ranking_1500flow' + '.png', dpi = 300)
plt.show()
