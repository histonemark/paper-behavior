"""
SIGMOIDAL LEARNING CURVES DURING TRAINING
Anne Urai, CSHL, 2019
"""

import pandas as pd
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
from paper_behavior_functions import *
import datajoint as dj
from IPython import embed as shell  # for debugging

# import wrappers etc
from ibl_pipeline import reference, subject, action, acquisition, data, behavior
from ibl_pipeline.utils import psychofit as psy
from ibl_pipeline.analyses import behavior as behavioral_analyses

# INITIALIZE A FEW THINGS
seaborn_style()
figpath = figpath()
pal = group_colors()
institution_map = institution_map()

# ================================= #
# GET DATA FROM TRAINED ANIMALS
# ================================= #

use_subjects = query_sessions()
b = (behavioral_analyses.BehavioralSummaryByDate * use_subjects)
behav = b.fetch(order_by='institution_short, subject_nickname, training_day',
                format='frame').reset_index()
behav['institution_code'] = behav.institution_short.map(institution_map)

# make sure each mouse starts at 0
# baseline correct with the first two days
for index, group in behav.groupby(['lab_name', 'subject_nickname']):
    behav['training_day'][behav.index.isin(
        group.index)] = group['training_day'] - group['training_day'].min()

# ================================= #
# LEARNING CURVES
# ================================= #

fig = sns.FacetGrid(behav,
                    hue="institution_code", palette=pal,
                    sharex=True, sharey=True, aspect=1, xlim=[0, 40])
fig.map(sns.lineplot, "training_day", "performance_easy")
fig.set_axis_labels('Training day', 'Performance (%) on easy trials')
# fig.set_titles("{col_name}")
fig.despine(trim=True)
fig.savefig(os.path.join(figpath, "figure2a_learningcurves_perlab.pdf"))
fig.savefig(os.path.join(
    figpath, "figure2a_learningcurves_perlab.png"), dpi=600)
plt.close('all')

# plot one curve for each animal, one panel per lab
fig = sns.FacetGrid(behav,
                    col="institution_code", col_wrap=4,
                    sharex=True, sharey=True, aspect=1, hue="subject_uuid", xlim=[0, 40])
fig.map(sns.lineplot, "training_day",
        "performance_easy", color='gray', alpha=0.7)
fig.set_axis_labels('Training day', 'Performance (%) on easy trials')
fig.set_titles("{col_name}")
for axidx, ax in enumerate(fig.axes.flat):
    ax.set_title(behav.institution_code.unique()[
                 axidx], color=pal[axidx], fontweight='bold')
fig.despine(trim=True)
fig.savefig(os.path.join(figpath, "figure2a_learningcurves_permouse.pdf"))
fig.savefig(os.path.join(
    figpath, "figure2a_learningcurves_permouse.png"), dpi=600)
plt.close('all')
