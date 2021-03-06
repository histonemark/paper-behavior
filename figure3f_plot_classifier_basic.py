#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot the results from the classification of lab by loading in the .pkl files generated by
figure3f_decoding_lab_membership_basic and figure3f_decoding_lab_membership_full

Guido Meijer
18 Jun 2020
"""

import pandas as pd
import numpy as np
import seaborn as sns
from os.path import join
import matplotlib.pyplot as plt
from paper_behavior_functions import seaborn_style, figpath, FIGURE_WIDTH, FIGURE_HEIGHT

# Which decoder to plot
FIG_PATH = figpath()
seaborn_style()

for DECODER in ['forest', 'bayes', 'regression']:  # forest, bayes or regression

    # Load in results from csv file
    decoding_result = pd.read_pickle(join('classification_results',
                                          'classification_results_basic_%s.pkl' % DECODER))

    # Calculate if decoder performs above chance
    chance_level = decoding_result['original_shuffled'].mean()
    significance = np.percentile(decoding_result['original'], 2.5)
    sig_control = np.percentile(decoding_result['control'], 0.001)
    if chance_level > significance:
        print('Classification performance not significanlty above chance')
    else:
        print('Above chance classification performance!')

    # %%

    # Plot
    f, ax1 = plt.subplots(1, 1, figsize=(FIGURE_WIDTH/5, FIGURE_HEIGHT))
    sns.violinplot(data=pd.concat([decoding_result['original'], decoding_result['control']], axis=1),
                   color=[0.6, 0.6, 0.6], ax=ax1)
    ax1.plot([-1, 2], [chance_level, chance_level], 'r--', zorder=-10)
    ax1.set(ylabel='Decoding (F1 score)', xlim=[-0.8, 1.4], ylim=[0, 0.62],
            xticklabels=['Decoding   \nof lab   ', '   Positive\n   control\n   (w. time zone)'])
    # ax1.text(0, 0.6, 'n.s.', fontsize=12, ha='center')
    # ax1.text(1, 0.6, '***', fontsize=15, ha='center', va='center')
    plt.text(0.7, np.mean(decoding_result['original_shuffled'])-0.1,
             'Chance\nlevel', color='r', fontsize=6)
    # plt.setp(ax1.xaxis.get_majorticklabels(), rotation=40)
    plt.tight_layout()
    sns.despine(trim=True)

    if DECODER == 'forest':
        plt.savefig(join(FIG_PATH, 'figure3f_decoding_%s_basic.pdf' % DECODER))
        plt.savefig(join(FIG_PATH, 'figure3f_decoding_%s_basic.png' % DECODER), dpi=300)
    else:
        plt.savefig(join(FIG_PATH, 'suppfig3_decoding_%s_basic.pdf' % DECODER))
        plt.savefig(join(FIG_PATH, 'suppfig3_decoding_%s_basic.png' % DECODER), dpi=300)

    # %%
    f, ax1 = plt.subplots(1, 1, figsize=(FIGURE_WIDTH/4, FIGURE_HEIGHT))
    n_labs = decoding_result['confusion_matrix'][0].shape[0]
    sns.heatmap(data=decoding_result['confusion_matrix'].mean(), vmin=0, vmax=0.6)
    ax1.plot([0, 7], [0, 7], '--w')
    ax1.set(xticklabels=np.arange(1, n_labs + 1), yticklabels=np.arange(1, n_labs + 1),
            ylim=[0, n_labs], xlim=[0, n_labs],
            title='', ylabel='Actual lab', xlabel='Predicted lab')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=40)
    plt.setp(ax1.yaxis.get_majorticklabels(), rotation=40)
    plt.gca().invert_yaxis()
    plt.tight_layout()

    plt.savefig(join(FIG_PATH, 'suppfig3_confusion_matrix_%s_basic.pdf' % DECODER))
    plt.savefig(join(FIG_PATH, 'suppfig3_confusion_matrix_%s_basic.png' % DECODER), dpi=300)

    f, ax1 = plt.subplots(1, 1, figsize=(FIGURE_WIDTH/4, FIGURE_HEIGHT))
    sns.heatmap(data=decoding_result['control_cm'].mean(), vmin=0, vmax=1)
    ax1.plot([0, 7], [0, 7], '--w')
    ax1.set(xticklabels=np.arange(1, n_labs + 1), yticklabels=np.arange(1, n_labs + 1),
            title='', ylabel='Actual lab', xlabel='Predicted lab',
            ylim=[0, n_labs], xlim=[0, n_labs])
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=40)
    plt.setp(ax1.yaxis.get_majorticklabels(), rotation=40)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(join(FIG_PATH, 'suppfig3_control_confusion_matrix_%s_basic.pdf' % DECODER))
    plt.savefig(join(FIG_PATH, 'suppfig3_control_confusion_matrix_%s_basic.png' % DECODER), dpi=300)
