import numpy as np  # Module that simplifies computations on matrices
import matplotlib.pyplot as plt  # Module used for plotting
from muselsl import list_muses, stream
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data
from scipy.signal import lfilter_zi, lfilter, butter
from tkinter import *

import data_parser as dp

NOTCH_B, NOTCH_A = butter(4, np.array([55, 65])/(256/2), btype='bandstop')

def update_buffer(data_buffer, new_data, notch=False, filter_state=None):
    """
    Concatenates "new_data" into "data_buffer", and returns an array with
    the same size as "data_buffer"
    """
    if new_data.ndim == 1:
        new_data = new_data.reshape(-1, data_buffer.shape[1])

    if notch:
        if filter_state is None:
            filter_state = np.tile(lfilter_zi(NOTCH_B, NOTCH_A),
                                   (data_buffer.shape[1], 1)).T
        new_data, filter_state = lfilter(NOTCH_B, NOTCH_A, new_data, axis=0,
                                         zi=filter_state)

    new_buffer = np.concatenate((data_buffer, new_data), axis=0)
    new_buffer = new_buffer[new_data.shape[0]:, :]

    return new_buffer, filter_state

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

if __name__ == '__main__':
    """ 1. CONNECT TO EEG STREAM """

    # # Search for active LSL stream
    # print('Looking for an EEG stream...')
    # muses = list_muses()
    # print(muses)
    # streams = stream(muses[0]['address'])

    """ 1. CONNECT TO EEG STREAM """

    # Search for active LSL stream
    print('Looking for an EEG stream...')
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    streams_gyro = resolve_byprop('type', 'GYRO', timeout=2)
    if len(streams_gyro) == 0:
        raise RuntimeError('Can\'t find EEG stream.')

    # Set active EEG & GYRO stream to inlet and apply time correction
    print("Start acquiring data")
    inlet = StreamInlet(streams[0], max_chunklen=12)
    inlet_gyro = StreamInlet(streams_gyro[0], max_chunklen=12)
    eeg_time_correction = inlet.time_correction()

    # EEG: Get the stream info, description, sampling frequency, number of channels
    info = inlet.info()
    description = info.desc()
    fs = int(info.nominal_srate())
    n_channels = info.channel_count()

    # GYRO: Get the stream info, description, sampling frequency, number of channels
    info_gyro = inlet_gyro.info()
    description_gyro = info_gyro.desc()
    fs_gyro = int(info_gyro.nominal_srate())
    n_channels_gyro = info_gyro.channel_count()

    ch_gyro = description_gyro.child('channels').first_child()
    ch_names_gyro = [ch_gyro.child_value('label')]

    # Get names of all channels
    ch = description.child('channels').first_child()
    ch_names = [ch.child_value('label')]
    for i in range(1, n_channels):
        ch = ch.next_sibling()
        ch_names.append(ch.child_value('label'))

    for i in range(1, n_channels_gyro):
        ch_gyro = ch_gyro.next_sibling()
        ch_names_gyro.append(ch_gyro.child_value('label'))
    print(ch_names)
    print(ch_names_gyro)

    """ 2. SET EXPERIMENTAL PARAMETERS """

    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    buffer_length = 2

    # Length of the epochs used to compute the FFT (in seconds)
    epoch_length = 1

    # Amount of overlap between two consecutive epochs (in seconds)
    overlap_length = 0.95

    # Amount to 'shift' the start of each next consecutive epoch
    shift_length = epoch_length - overlap_length

    # Index of the channel (electrode) to be used
    # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
    index_channel = [0, 1, 2, 3]
    # # Name of our channel for plotting purposes
    # ch_names = [ch_names[i] for i in index_channel]
    # n_channels = len(index_channel)
    #
    # # Get names of features
    # # ex. ['delta - CH1', 'pwr-theta - CH1', 'pwr-alpha - CH1',...]
    # feature_names = BCIw.get_feature_names(ch_names)

    """3. INITIALIZE BUFFERS """
    # Initialize raw EEG data buffer (for plotting)
    eeg_buffer = np.zeros((int(fs * buffer_length), n_channels))
    gyro_buffer = np.zeros((int(fs * buffer_length), n_channels_gyro))
    filter_state = None  # for use with the notch filter

    # create a tkinter window and built same-size canvas in it
    CANVAS_WIDTH = 1080
    CANVAS_HEIGHT = 720
    app = Tk()
    app.geometry(str(CANVAS_WIDTH) + "x" + str(CANVAS_HEIGHT))
    canvas = Canvas(app, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
    canvas.pack(pady=20)
    lasx = CANVAS_WIDTH / 2
    lasy = CANVAS_HEIGHT / 2

    try:
        # The following loop does what we see in the diagram of Exercise 1:
        # acquire data, compute features, visualize raw EEG and the features
        while True:
            """ 3.1 ACQUIRE DATA """
            # Obtain EEG data from the LSL stream
            eeg_data, timestamp = inlet.pull_chunk(
                timeout=1, max_samples=int(shift_length * fs))

            # Obtain EEG data from the LSL stream
            gyro_data, timestamp = inlet_gyro.pull_chunk(
                timeout=1, max_samples=int(shift_length * fs))

            # Only keep the channel we're interested in
            print(np.shape(eeg_data))
            ch_data = np.array(eeg_data)[:, index_channel]
            ch_data_gyro = np.array(gyro_data)

            # print(ch_data)
            # print(ch_data_gyro)
            gyros, colors = dp.data_stream(ch_data_gyro, ch_data)
            for idx in range(len(gyros)):
                cur_offset = gyros[idx]
                cur_color = colors[idx]
                scalar_x, scalar_y = dp.get_correcting_scalar(CANVAS_WIDTH, CANVAS_HEIGHT, lasx, lasy)
                if lasx > 0.5 * CANVAS_WIDTH and cur_offset[1] < 0 \
                or lasx < 0.5 * CANVAS_WIDTH and cur_offset[1] > 0:
                    cur_offset[1] *= scalar_x
                if lasy > 0.5 * CANVAS_HEIGHT and cur_offset[0] < 0 \
                or lasy < 0.5 * CANVAS_HEIGHT and cur_offset[0] > 0:
                    cur_offset[0] *= scalar_y
                new_x = max(0, min(lasx + cur_offset[1], CANVAS_WIDTH))
                new_y = max(0, min(lasy + cur_offset[0], CANVAS_HEIGHT))
                canvas.create_line((lasx, lasy, new_x, new_y),
                      fill=_from_rgb((cur_color[0], cur_color[1], cur_color[2])),
                      width=7)
                print(lasx, lasy, cur_offset[0], cur_offset[1])
                app.update_idletasks()
                app.update()
                lasx = new_x
                lasy = new_y

            # # Update EEG buffer
            # eeg_buffer, filter_state = update_buffer(
            #     eeg_buffer, ch_data, notch=True,
            #     filter_state=filter_state)

            # """ 3.3 VISUALIZE THE RAW EEG AND THE FEATURES """
            # plotter_eeg.update_plot(eeg_buffer)
            # plotter_feat.update_plot(feat_buffer)
            # plt.pause(0.00001)


    except KeyboardInterrupt:

        print('Closing!')