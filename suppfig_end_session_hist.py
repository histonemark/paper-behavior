"""
HISTOGRAM OF SESSION END STATUSES DURING TRAINING
Miles  Wells, UCL, 2019
"""

import datajoint as dj
from ibl_pipeline import acquisition
from paper_behavior_functions import \
    (figpath, query_sessions, query_subjects, group_colors, seaborn_style)
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set default figure size.
plt.rcParams['figure.figsize'] = (8, 5)
save_path = figpath()  # Our figure save path
colors = group_colors()
seaborn_style()

endcriteria = dj.create_virtual_module('SessionEndCriteria', 'group_shared_end_criteria')
sessions = query_sessions().proj(session_start_date='date(session_start_time)')
subj_crit = query_subjects().aggr(
                     acquisition.Session(),
                     first_day='min(date(session_start_time))').proj('first_day')
session_num = (sessions * subj_crit).proj(n='DATEDIFF(session_start_date, first_day)')

df = (endcriteria.SessionEndCriteria * session_num).fetch(format='frame')  # Fetch data

# Convert statuses to numerical
plt.figure()
ids = {k[0]: v for v, k in enumerate(endcriteria.EndCriteria.fetch())}
del ids['perf<40']
df['end_status_id'] = df['end_status'].map(ids)
df['end_status_id'][df['end_status_id'] == 4] = 5
bins = [0, 6, 13, 20, 27, 34]
ax = df.pivot(columns='end_status_id').n.plot(
    kind='hist', color=colors, bins=bins, stacked=True, density=True)  # weights=369,
ax.legend(ids.keys())
ax.set_xlabel('Session #', labelpad=15)
ax.set_ylabel('Frequency', labelpad=15)
plt.gcf().savefig(os.path.join(save_path, "suppfig_end_status_histogram.png"))

# Unity plot
max_n_days = 7*3
normalize = True
df = df.reset_index()
counts = np.array([[sum(df['end_status_id'].where(df['n'] == n_days) == criterion)
                    if n_days < max_n_days
                    else sum(df['end_status_id'].where(df['n'] >= n_days) == criterion)
                    for n_days in range(max_n_days+1)]
                   for criterion in np.sort(df['end_status_id'].unique())])

if normalize:
    counts = np.stack([n / sum(n) for n in counts.T]).T
    #  counts = np.stack([n / sum(n) for n in counts])

bar_l = range(1, counts.shape[1]+1)
#  bottom = np.zeros_like(bar_l).astype('float')
bottom = np.vstack((np.zeros((1, counts.shape[1])), np.cumsum(counts, axis=0)[:-1, :]))
plt.figure()
ax = plt.gca()
for i in range(counts.shape[0]):
    ax.bar(bar_l, counts[i, :], bottom=bottom[i, :], width=1, label=list(ids.keys())[i],
           color=colors[i])

ax.set_xticks([1] + [i * 7 for i in range(1, round(max_n_days+7/7))])
ax.set_xlim([.5, counts.shape[1]+.5])
ax.set_xlabel('Session #', labelpad=15)
ax.set_ylabel('Proportion', labelpad=15)

ax.legend()
plt.gcf().savefig(os.path.join(save_path, "suppfig_end_status_histogram_normalized.png"))
