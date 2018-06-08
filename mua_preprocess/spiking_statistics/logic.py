from spiking_statistics.funcs import *


def main(ops):
    df_list = []
    for recording in ops.recordings_to_analyse:
        df = load_data(recording=recording,
                       data_dir=ops.data_dir,
                       verbose=ops.verbose)
        df = manipulate_df(df)
        max_times, n_conditions = get_condition_times(df, experiment=ops.experiment)
        if n_conditions == 1:
            max_time = max_times[0][1]
        elif n_conditions == 2:
            max_time = max_times[1][1]
        # baseline_stats
        df_base = df[df['condition'] == 'Baseline']
        df_ts = create_time_series(df_base)
        cv_isis_ts = df_ts.apply(func=calculate_neuron_cov,
                                 num_mins_per_bin=2,
                                 total_time=60)
        mean_firing_rates_ts = df_ts.apply(func=calculate_neuron_mfr,
                                           num_mins_per_bin=2,
                                           total_time=60)
        cov_medians = get_medians(df=cv_isis_ts, lab='CV ISI')
        mfr_medians = get_medians(df=mean_firing_rates_ts, lab='Firing Rate')
        df_stats = cov_medians.join(mfr_medians)
        df_stats['recording'] = recording

        # all neurons - calculate firing rate and cv-isi over time then plot
        df_ts_all = create_time_series(df)
        cv_isis_ts = df_ts_all.apply(func=calculate_neuron_cov,
                                     num_mins_per_bin=2,
                                     total_time=np.int(max_time / 60))
        mean_firing_rates_ts = df_ts_all.apply(func=calculate_neuron_mfr,
                                               num_mins_per_bin=2,
                                               total_time=np.int(max_time / 60))
        plot_cluster(dfs=[mean_firing_rates_ts, cv_isis_ts],
                     max_time=max_time,
                     df_base=df_ts,
                     experiment=ops.experiment,
                     medians=[df_stats['Firing Rate'], df_stats['CV ISI']],
                     labs=['Firing Rate [Hz]', 'CV-ISI'],
                     fig_folder=ops.fig_folder,
                     n_conditions=n_conditions)
        df_list.append(df_stats)
    df_merged = pd.concat(df_list)
    df_merged.reset_index(inplace=True)
    df_merged.index = range(len(df_merged))
    mkdirs_(ops.temp_folder)
    df_merged.to_csv(''.join([os.path.join(ops.temp_folder, 'spike_stats'), '.csv']), index=False)
