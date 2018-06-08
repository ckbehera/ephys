import os
import pandas as pd
import numpy as np
from quantities import ns, s
from neo.core import SpikeTrain
from elephant.statistics import isi, cv, mean_firing_rate
import matplotlib.pyplot as plt
plt.style.use('ggplot')


def load_data(recording, data_dir, verbose):
    if verbose:
        print('Loading data:\t{}'.format(recording))
    path = ''.join([os.path.join(data_dir, recording, recording), '.csv'])
    return pd.read_csv(path)


def manipulate_df(df):
    df['spike'] = 1
    df['time'] = pd.to_timedelta(df['time'], unit='s')
    return df


def create_time_series(df):
    df = df.pivot_table(index='time',
                        columns='spike_cluster',
                        values='spike',
                        aggfunc='count')
    return df


def get_condition_times(df, experiment):
    if experiment == 'DREADD':
        max_time = df[df['condition'] == 'CNO']['time'].iloc[-1].total_seconds()
        n_conditions = 1
    if experiment == 'CIT':
        max_time_cit = df[df['condition'] == 'CIT']['time'].iloc[-1].total_seconds()
        if 'WAY' in df['condition'].values:
            max_time_way = df[df['condition'] == 'WAY']['time'].iloc[-1].total_seconds()
            n_conditions = 2
        else:
            max_time_way = max_time_cit
            n_conditions = 1
        max_time = list(zip(['CIT', 'WAY'], [max_time_cit, max_time_way]))
    return max_time, n_conditions


def calculate_neuron_cov(col, num_mins_per_bin, total_time):
    num_bins = np.int(total_time / num_mins_per_bin)
    col_bins = np.array_split(col, num_bins)
    cv_isis = pd.Series(np.zeros(num_bins))

    for ind, col_bin in enumerate(col_bins):
        spike_times = pd.to_numeric(col_bin[col_bin.notnull()].index.values)
        try:
            spike_train = SpikeTrain(times=spike_times,
                                     t_stop=spike_times[-1],
                                     units=ns)
            plt.tight_layout()
            cv_isi = cv(isi(spike_train))
        except IndexError:
            cv_isi = np.nan
        cv_isis[ind] = cv_isi

    return cv_isis


def calculate_neuron_mfr(col, num_mins_per_bin, total_time):
    num_bins = np.int(total_time / num_mins_per_bin)
    col_bins = np.array_split(col, num_bins)
    mfrs = pd.Series(np.zeros(num_bins))

    for ind, col_bin in enumerate(col_bins):
        spike_times = pd.to_numeric(col_bin[col_bin.notnull()].index.values)
        try:
            spike_train = SpikeTrain(times=spike_times,
                                     t_stop=spike_times[-1],
                                     units=ns)
            mfr = mean_firing_rate(spike_train)
        except IndexError:
            mfr = np.nan
        mfrs[ind] = mfr
    mfrs *= 10**10
    return mfrs


def get_medians(df, lab):
    empty = np.zeros(len(df.columns))
    for col in range(len(df.columns)):
        vals = df.iloc[:, col].dropna().values
        med = np.median(vals)
        empty[col] = med
    df = pd.DataFrame({lab: empty}, index=df.columns)
    return df


def plot_cluster(dfs, max_time, experiment, df_base, fig_folder, medians, n_conditions, labs=['Firing Rate', 'CV-ISI']):
    num_mins = np.int(max_time / 60)

    if experiment == 'CIT':
        condition_lab_1 = 'Citalopram'
        condition_lab_2 = 'WAY'

    elif experiment == 'DREADD':
        condition_lab_1 = 'CNO'

    for col in range(len(dfs[0].columns)):
        # New set of plots for each column (for each cluster)
        f, a = plt.subplots(figsize=(12, 12), nrows=3)

        for ind, df in enumerate(dfs):
            # Plot Firing rate and CV ISI over time
            x = np.linspace(0, num_mins, len(df))
            y = df.iloc[:, col]
            a[ind].plot(x, y, linewidth=1.5)

            # Plot line for median Firing rate
            line_y = np.ones(10) * medians[ind].iloc[col]
            line_x = np.linspace(1, num_mins, 10)
            a[ind].plot(line_x, line_y, linestyle='--', color='k',
                        label='Median {lab}:{num}'.format(lab=labs[ind], num=str(np.round(medians[ind].iloc[col], 2))))

            # Set condition indicators
            condition_indecator_y = (np.ones(2) * np.max(df.iloc[:, col])) + 1
            condition_indecator_x = np.linspace(60, num_mins, 2)
            a[ind].plot(condition_indecator_x, condition_indecator_y, linewidth=4, label=(condition_lab_1))

            # Indicate WAY if data from CIT experiment
            if n_conditions == 2 and experiment == 'CIT':
                condition_indecator_x = np.linspace(120, num_mins, 2)
                condition_indecator_y = (np.ones(2) * np.max(df.iloc[:, col])) + 0.3
                a[ind].plot(condition_indecator_x, condition_indecator_y, linewidth=4, label=(condition_lab_2))

            a[ind].set_title('{lab} over time.\nCluster {clus}'. format(clus=df.columns[col], lab=labs[ind]))

            # Set plot aesthetics
            a[ind].set_ylabel(labs[ind])
            a[ind].set_xlabel('Time [minutes]')
            a[ind].fill_between(x, y, alpha=0.4)
            a[ind].legend()

        if not os.path.exists(fig_folder):
            os.mkdir(fig_folder)

        spike_times = pd.to_numeric(df_base.iloc[:, col][df_base.iloc[:, col].notnull()].index.values) / 10**10
        spike_train = SpikeTrain(times=spike_times,
                                 t_stop=spike_times[-1],
                                 units=s)
        isis = isi(spike_train)
        isis = np.array(isis) * 10
        a[2].hist(isis, bins=np.int(len(isis) / 4), alpha=0.8)
        a[2].set_title('Inter Spike Interval Histogram')
        a[2].set_xlim([0, 3.5])
        a[2].set_xlabel('Time [Seconds]')
        plt.tight_layout()
        plt.savefig(''.join([os.path.join(fig_folder, str(col)), '.png']))
        plt.close()


def mkdirs_(path):
    if not os.path.exists(path):
        os.mkdir(path)