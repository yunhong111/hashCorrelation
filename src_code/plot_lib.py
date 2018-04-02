import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot(data, x=None, k=1, errors=[], xlabel='x', ylabel='y', title='title', 
        xlog=False, ylog=False, acc_legend=[], xticks=[], 
        figure_width=4.3307*1.25, figure_height=3.346*1.25, legend_y=0.3, 
        x_shift=0.02, y_shift=0.02, legend_x=0.6
    ):
            
    fig = plt.figure(figsize=(figure_width, figure_height))
    ax = plt.subplot(111)
    types = ['o-', '^-.', '*--', 'd-.', 'p:', '>:', '<-', '8-',
            's-', 'p-', '1-', '2-', '3-', '4-', 'h-']
    colors = ['b', 'r', 'g', 'm', 'c', 'k',  
                '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
    if ylog:
        ax.set_yscale('log')
    if xlog:
        ax.set_xscale('log')
    
    if k == 1:
        if len(x) == 0:
            x_values = np.arange(len(data))
        plt.plot(x_values, data, 'o-', color='blue', markersize=8)
        if len(errors) != 0:
            plt.errorbar(x_values, data, errors, linestyle='None',color="r")
    else:
        for i in range(len(data)):
            if len(x) == 0:
                x_values = np.arange(len(data[i]))
            else:
                x_values = x
            
            if len(x) !=0 and isinstance(x[0], (list,)):
                x_values = x[i]
            print 'x_values, data[i]',x_values, data[i]
                
            plt.plot(
                x_values, data[i], types[i], color=colors[i], linewidth=2.0, markersize=10)
            if len(errors) != 0:
                plt.errorbar(
                    x_values, 
                    data[i], yerr=errors[i], 
                    linestyle='None',
                    color=colors[i%16],
                    linewidth=1.5,
                    capthick=3
                )

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    if len(xticks) > 0:
        plt.xticks(x_values, xticks)
    
    plt.grid(True)
    box = ax.get_position()
    ax.set_position(
        [box.x0+x_shift, box.y0+y_shift, box.width*1, box.height*1])
    #plt.xticks(flow_num)
    
    # Put a legend to the right of the current axis
    if len(acc_legend) != 0:
        ax.legend(
            acc_legend, loc='center left', 
            bbox_to_anchor=(legend_x, legend_y), 
            numpoints=1
    )
    #plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    print '../figures/' + title + '.png'
    fig.savefig('../figures/' + title + '.png', dpi = 300)
    
def box_plot(data, x=None, k=1, errors=[], xlabel='x', ylabel='y', title='title', 
        xlog=False, ylog=False, acc_legend=[], xticks=[], 
        figure_width=4.3307*1.25, legend_y=0.3
    ):
            
    fig = plt.figure(figsize=(figure_width, 3.346*1.25))
    ax = plt.subplot(111)
    types = ['o-', '^-.', '*--', 'd-.', 'p:', '>:', '<-', '8-',
            's-', 'p-', '1-', '2-', '3-', '4-', 'h-']
    colors = ['b', 'r', 'g', 'm', 'c', 'k',  
                '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c',
                  '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
                  '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f',
                  '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
    if ylog:
        ax.set_yscale('log')
    if xlog:
        ax.set_xscale('log')
    
    bplots = []
    colors = ['pink', 'lightblue', 'lightgreen']
    for i in range(len(data)):
        x_values = np.arange(len(data[i]))
        bplot1 = plt.boxplot(
            data[i], widths=0.3, patch_artist=True)
        
        for patch in bplot1['boxes']:
            patch.set_facecolor(colors[i])
        bplots.append(bplot1)
    
    """for bplot in bplots:
        for patch in bplot['boxes']:
            patch.set_facecolor(colors[0])"""
            
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    if len(xticks) > 0:
        plt.xticks(np.arange(1, len(data[0])+1), xticks)
    
    plt.grid(True)
    box = ax.get_position()
    ax.set_position(
        [box.x0+0.04, box.y0+0.02, box.width, box.height])
    fig.savefig('../figures/' + title + 'boxplot.png', dpi = 300)
