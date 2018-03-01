import matplotlib.pyplot as plt
import pandas as pd

flow_num = [5000*i for i in range(1, 6)]
df = pd.read_csv('../outputs/chern_values.csv', names=['a'+str(i) for i in range(5)])

print df.iloc[0:5]


# Plot
fig = plt.figure(figsize=(4.3307, 3.346))
ax = plt.subplot(111)
types = ['o-', '^-', '*-', '<-', '>-', '+-']
colors = ['b', 'r', 'g', 'm', 'c', 'k']
for i in range(6):
    plt.plot(flow_num, df['a4'].iloc[i*5:(i+1)*5], types[i], color=colors[i])
    #plt.plot(flow_num, mark_first_web_acc, '^-', color='red')
    #plt.plot(flow_num, mark_first_hadoop_acc, '*-', color='green')

plt.ylabel('Chernoff value (C_b)')
plt.xlabel('The number of flows')
plt.grid(True)
box = ax.get_position()
ax.set_position([box.x0+0.02, box.y0+0.15, box.width * 0.75, box.height*0.75])
plt.xticks(flow_num)
# Put a legend to the right of the current axis
acc_legend = ['Web', '100', '500', '1000', '5%', '10%']
ax.legend(acc_legend, loc='center left', bbox_to_anchor=(0.96, 0.3), numpoints=1)
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
fig.savefig(
    '/home/yunhong/Research_4/trunk/figures/chern_values' + '.png', dpi = 300)
plt.show()



