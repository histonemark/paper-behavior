"""
Plotting of behavioral metrics during the full task (biased blocks) per lab

Guido Meijer
6 May 2020
"""

import seaborn as sns
import numpy as np
from os.path import join
import matplotlib.pyplot as plt
from paper_behavior_functions import (figpath, seaborn_style, group_colors,
                                      query_sessions_around_criterion, institution_map,
                                      FIGURE_WIDTH, FIGURE_HEIGHT)
from ibl_pipeline import reference, subject, behavior
from dj_tools import fit_psychfunc, dj2pandas
import pandas as pd

# Initialize
fig_path = figpath()
pal = group_colors()
seaborn_style()
institution_map, col_names = institution_map()
col_names = col_names[:-1]

# %% query sessions
use_sessions = query_sessions_around_criterion(criterion='ephys', days_from_criterion=[2, 0])[0]
b = (use_sessions * subject.Subject * subject.SubjectLab * reference.Lab * behavior.TrialSet.Trial
     & 'task_protocol LIKE "%biased%"')

# load data into pandas dataframe
b2 = b.proj('institution_short', 'subject_nickname', 'task_protocol',
            'trial_stim_contrast_left', 'trial_stim_contrast_right', 'trial_response_choice',
            'task_protocol', 'trial_stim_prob_left', 'trial_feedback_type',
            'trial_response_time', 'trial_stim_on_time', 'time_zone')
bdat = b2.fetch(order_by='institution_short, subject_nickname, session_start_time, trial_id',
                format='frame').reset_index()
behav = dj2pandas(bdat)
behav['institution_code'] = behav.institution_short.map(institution_map)

# exclude contrasts that were part of a pilot with a different contrast set
behav = behav[((behav['signed_contrast'] != -8) & (behav['signed_contrast'] != -4)
               & (behav['signed_contrast'] != 4) & (behav['signed_contrast'] != 8))]

biased_fits = pd.DataFrame()
for i, nickname in enumerate(behav['subject_nickname'].unique()):
    if np.mod(i+1, 10) == 0:
        print('Processing data of subject %d of %d' % (i+1,
                                                       len(behav['subject_nickname'].unique())))

    # Get lab
    lab = behav.loc[behav['subject_nickname'] == nickname, 'institution_code'].unique()[0]

    # Fit psychometric curve
    left_fit = fit_psychfunc(behav[(behav['subject_nickname'] == nickname)
                                   & (behav['probabilityLeft'] == 80)])
    right_fit = fit_psychfunc(behav[(behav['subject_nickname'] == nickname)
                                    & (behav['probabilityLeft'] == 20)])
    fits = pd.DataFrame(data={'threshold_l': left_fit['threshold'],
                              'threshold_r': right_fit['threshold'],
                              'bias_l': left_fit['bias'],
                              'bias_r': right_fit['bias'],
                              'lapselow_l': left_fit['lapselow'],
                              'lapselow_r': right_fit['lapselow'],
                              'lapsehigh_l': left_fit['lapsehigh'],
                              'lapsehigh_r': right_fit['lapsehigh'],
                              'nickname': nickname, 'lab': lab})
    biased_fits = biased_fits.append(fits, sort=False)

# %% Plot metrics

f, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(16, 4))
lab_colors = group_colors()

ax1.plot([10, 20], [10, 20], linestyle='dashed', color=[0.6, 0.6, 0.6])
for i, lab in enumerate(biased_fits['lab'].unique()):
    ax1.errorbar(biased_fits.loc[biased_fits['lab'] == lab, 'threshold_l'].mean(),
                 biased_fits.loc[biased_fits['lab'] == lab, 'threshold_r'].mean(),
                 xerr=biased_fits.loc[biased_fits['lab'] == lab, 'threshold_l'].sem(),
                 yerr=biased_fits.loc[biased_fits['lab'] == lab, 'threshold_l'].sem(),
                 fmt='s', color=lab_colors[i])
ax1.set(xlabel='80:20 block', ylabel='20:80 block', title='Threshold')

ax2.plot([0, 0.1], [0, 0.1], linestyle='dashed', color=[0.6, 0.6, 0.6])
for i, lab in enumerate(biased_fits['lab'].unique()):
    ax2.errorbar(biased_fits.loc[biased_fits['lab'] == lab, 'lapselow_l'].mean(),
                 biased_fits.loc[biased_fits['lab'] == lab, 'lapselow_r'].mean(),
                 xerr=biased_fits.loc[biased_fits['lab'] == lab, 'lapselow_l'].sem(),
                 yerr=biased_fits.loc[biased_fits['lab'] == lab, 'lapselow_r'].sem(),
                 fmt='s', color=lab_colors[i])
ax2.set(xlabel='80:20 block', ylabel='20:80 block', title='Lapse left')

ax3.plot([0, 0.1], [0, 0.1], linestyle='dashed', color=[0.6, 0.6, 0.6])
for i, lab in enumerate(biased_fits['lab'].unique()):
    ax3.errorbar(biased_fits.loc[biased_fits['lab'] == lab, 'lapsehigh_l'].mean(),
                 biased_fits.loc[biased_fits['lab'] == lab, 'lapsehigh_r'].mean(),
                 xerr=biased_fits.loc[biased_fits['lab'] == lab, 'lapsehigh_l'].sem(),
                 yerr=biased_fits.loc[biased_fits['lab'] == lab, 'lapsehigh_l'].sem(),
                 fmt='s', color=lab_colors[i])
ax3.set(xlabel='80:20 block', ylabel='20:80 block', title='Lapse right')

ax4.plot([-10, 10], [-10, 10], linestyle='dashed', color=[0.6, 0.6, 0.6])
for i, lab in enumerate(biased_fits['lab'].unique()):
    ax4.errorbar(biased_fits.loc[biased_fits['lab'] == lab, 'bias_l'].mean(),
                 biased_fits.loc[biased_fits['lab'] == lab, 'bias_r'].mean(),
                 xerr=biased_fits.loc[biased_fits['lab'] == lab, 'bias_l'].sem(),
                 yerr=biased_fits.loc[biased_fits['lab'] == lab, 'bias_l'].sem(),
                 fmt='s', color=lab_colors[i])
ax4.set(xlabel='80:20 block', ylabel='20:80 block', title='Bias')

plt.tight_layout(pad=2)
seaborn_style()
plt.savefig(join(fig_path, 'figure4e-h_metrics_per_lab_full.pdf'), dpi=300)
plt.savefig(join(fig_path, 'figure4e-h_metrics_per_lab_full.png'), dpi=300)
