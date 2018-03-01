import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot(data, x=None, k=1, errors=[], xlabel='x', ylabel='y', title='title', 
        xlog=False, ylog=False, acc_legend=[], xticks=[], 
        figure_width=4.3307*1.25, legend_y=0.3
    ):
            
    fig = plt.figure(figsize=(figure_width, 3.346*1.25))
    ax = plt.subplot(111)
    types = ['o-', '^-.', '*--', 'd-', 'p-', '>-', '<-', '8-',
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
        if x == None:
            x_values = np.arange(len(data))
        plt.plot(x_values, data, 'o-', color='blue')
        if len(errors) != 0:
            plt.errorbar(x_values, data, errors, linestyle='None',color="r")
    else:
        for i in range(len(data)):
            if x == None:
                x_values = np.arange(len(data[i]))
            else:
                x_values = x
            plt.plot(
                x_values, data[i], types[i], color=colors[i], linewidth=1.5)
            if len(errors) != 0:
                plt.errorbar(
                    x_values, 
                    data[i], errors[i], 
                    linestyle='None',
                    color=colors[i%16],
                    linewidth=1.5,
                    capthick=2
                )

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    if len(xticks) > 0:
        plt.xticks(x_values, xticks)
    
    plt.grid(True)
    box = ax.get_position()
    ax.set_position(
        [box.x0+0.04, box.y0+0.15, box.width * 0.8, box.height*0.8])
    #plt.xticks(flow_num)
    
    # Put a legend to the right of the current axis
    if len(acc_legend) != 0:
        ax.legend(
            acc_legend, loc='center left', 
            bbox_to_anchor=(0.6, legend_y), 
            numpoints=1
    )
    #plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right')
    fig.savefig('../figures/' + title + '.png', dpi = 300)
    
def box_plot(data, x=None, k=1, errors=[], xlabel='x', ylabel='y', title='title', 
        xlog=False, ylog=False, acc_legend=[], xticks=[], 
        figure_width=4.3307*1.25, legend_y=0.3
    ):
            
    fig = plt.figure(figsize=(figure_width, 3.346*1.25))
    ax = plt.subplot(111)
    types = ['o-', '^-.', '*--', 'd-', 'p-', '>-', '<-', '8-',
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
        
    for i in range(len(data)):
        x_values = np.arange(len(data[i]))
        plt.boxplot(
            data[i])
    
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)

    if len(xticks) > 0:
        plt.xticks(np.arange(1, len(data[0])+1), xticks)
    
    plt.grid(True)
    box = ax.get_position()
    ax.set_position(
        [box.x0+0.04, box.y0+0.15, box.width * 0.8, box.height*0.8])
    fig.savefig('../figures/' + title + 'boxplot.png', dpi = 300)
