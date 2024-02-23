import matplotlib.pyplot as plt
from pprint import pprint
from collections import Counter, defaultdict
import pandas as pd

def plot_distribution_pie(data:'list', fname='fig.png'):

    counter = Counter(data)
    labels = counter.keys()
    sizes = counter.values()

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Distribution')
    plt.savefig(fname)
    plt.clf()

def plot_distribution_hist(data, fname='fig.png'):
    plt.hist(data, bins=10, edgecolor='black')  # You can adjust the number of bins as needed
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Distribution')
    plt.grid(True)
    plt.savefig(fname)
    plt.clf()

def plot_rspdistribution_stacked_hist(data, fname='stacked.png'):
    """
    Plot the stacked histogram.
    It is usually used for plotting distribution (e.g., response code distribution for different ZCL commands)
    """
    assert(isinstance(data, dict))
    cmd_ids:'list[str]' = list(data.keys())
    # 1. Identify the union set of all rspCodes for different command execution
    rspCodes = set()
    for cmd_id, val_list in data.items():
        for (rspCode, percentage) in val_list:
            rspCodes.add(rspCode)
    # 2. Construct the percentage list for each command
    cmdCodeDist = defaultdict(list)
    for cmd_id in cmd_ids:
        for rspCode in rspCodes:
            codeItems = [x for x in data[cmd_id] if x[0] == rspCode]
            percentage = 0 if len(codeItems) == 0 else codeItems[0][1]
            cmdCodeDist[cmd_id].append(percentage)
    
    df_components = []
    for cmd_id, percentage_list in cmdCodeDist.items():
        newlist = [cmd_id] + percentage_list
        df_components.append(newlist)
    
    df = pd.DataFrame(df_components, columns=['cmdID']+list(rspCodes))
    df.plot(x='cmdID', kind='bar', stacked=True, title='rspCode distribution for different commands')
    plt.savefig(fname)
    plt.clf()