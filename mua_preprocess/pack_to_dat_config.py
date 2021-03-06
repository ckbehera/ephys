from pack_to_dat.classes import Options
from pack_to_dat.pack_continuous_logic import main
'''

This script converts many .continuous files to one .dat file

Change the following parameters:
    openephys_folder = root directory containing subdirectories containing .continuous files

    recordings_to_pack = list of subdirecotry names (containing .continuous files)
                         within openephys_folder of the recordings you wish to pack

    dat_folder = root output folder for the packed .dat file

    chan_map = rearrange channel labels such that channels most physically
               close to each other have consecutive labels
               N.B. only use this if the channel map is not already configured during
               the recordings

    ref_method = Once the data is packed to a single dat file, a filter can be
                 applied to increase the quality of the signal. Choose an
                 integer to subtract that channel from all others. Use ave to
                 apply a common average reference.

    operating_system = the operating_system on which the sript is being run
                       choose 'win' or 'unix'


ROS 2018

'''


cambridge_chan_map = [22, 17, 28, 25, 29, 26, 20, 23,
                      21, 27, 31, 18, 30, 19, 24, 32,
                      6, 1, 12, 9, 13, 10, 4, 7, 5, 11,
                      15, 2, 14, 3, 8, 16]

ops = Options(recordings_to_pack=['CIT_06_2018-06-13_14-29-45_PRE',
                                  'CIT_06_2018-06-13_15-31-11_CIT',
                                  'CIT_06_2018-06-13_16-32-48_WAY',
                                  'CIT_07_2018-06-14_15-03-20_PRE',
                                  'CIT_07_2018-06-14_16-04-02_CIT'],
              openephys_folder=r'C:\Users\Rory\raw_data\CIT_WAY\continuous',
              dat_folder=r'C:\Users\Rory\raw_data\CIT_WAY\dat_files',
              chan_map=cambridge_chan_map,
              ref_method='ave',
              operating_system='win',
              verbose=True)

if __name__ == '__main__':
    main(ops)
