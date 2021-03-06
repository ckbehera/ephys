from cluster_heatmap.logic import main
from cluster_heatmap.classes import Options


ops = Options(csv_dir=r'F:\SERT_DREAD\Combined_binary_files_probe\csvs',
              csv_file_name='all_neurons_ts_with_clusters',
              out_folder=r'F:\SERT_DREAD\Combined_binary_files_probe\figures\cluster_heat_maps',
              resample_period='5sec',
              category_column='category',
              rolling_periods=120,
              normalisation_method='percent',
              vmin=0,
              vmax=200)

if __name__ == '__main__':
    main(ops)
