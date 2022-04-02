# Muse 2 data parser
from queue import Queue

AVG_WINDOW = 9       # averaging/smoothing value among the neighboring X datapoints
GYRO_HI_THRES = 8   # smoothed speed is set to 0 if below this value
GYRO_LO_THRES = -8  # AND above this value
DELTA_T = 1

GYRO_Y = Queue(maxsize=AVG_WINDOW+1)
GYRO_Z = Queue(maxsize=AVG_WINDOW+1)

def extract_speed(input):
    """
    Take a gyro speed datapoint, extract and return the y, z value
    y: 正低头，负抬头
    x: 正左旋，负右旋
    """
    return input[1], input[2]

def process_gyro(input):
    """
    Take a gyro speed datapoint, calculate the smoothed datapoint that's AVG_RANGE
    earlier, turn it to offset and output
    """
    y, z = extract_speed(input)
    GYRO_Y.put(y)
    GYRO_Z.put(z)
    if GYRO_Y.qsize() == AVG_WINDOW:     # smooth the middle value
        sum_y = sum_z = 0
        for _ in range(AVG_WINDOW):
            cur_y = GYRO_Y.get()
            cur_z = GYRO_Z.get()
            sum_y += cur_y
            sum_z += cur_z
            GYRO_Y.put(cur_y)
            GYRO_Z.put(cur_z)
        smoothed_y = sum_y / AVG_WINDOW
        smoothed_z = sum_z / AVG_WINDOW
        GYRO_Y.get()        # remove the first element from the queues
        GYRO_Z.get()
        if smoothed_y >= GYRO_LO_THRES and smoothed_y <= GYRO_HI_THRES: smoothed_y = 0
        if smoothed_z >= GYRO_LO_THRES and smoothed_z <= GYRO_HI_THRES: smoothed_z = 0
        return smoothed_y * DELTA_T, smoothed_z * DELTA_T
    else: return 0, 0


def extract_channels(input):
    """
    Take a neural datapoint, extract and return three usable channels for mapping
    """
    return input[1], input[2], min(input[0], input[3])

def channel_to_color(channel):
    """
    Given a channel and its value, map to a number between 0 to 255 and return it
    """
    return int(min(255, abs(channel)))

def process_color(input):
    """
    Take a neural datapoint, change the channel values into RGB values
    return the three RGB values
    """
    ch_R, ch_G, ch_B = extract_channels(input)
    R = channel_to_color(ch_R)
    G = channel_to_color(ch_G)
    B = channel_to_color(ch_B)
    return R, G, B


def data_stream(gyro_stream, color_stream):
    """
    Take the stream of input data,
    Output the stream of gyro offsets and the stream of colors to the canvas module
    """
    gyro = []
    color = []
    for i in range(len(gyro_stream)):
        gyro.append(process_gyro(gyro_stream[i]))
        color.append(process_color(color_stream[i]))
    return gyro, color