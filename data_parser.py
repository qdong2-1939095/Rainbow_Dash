# Muse 2 data parser
from queue import Queue

AVG_WINDOW = 9       # averaging/smoothing value among the neighboring X datapoints
GYRO_HI_THRES = 8   # smoothed speed is set to 0 if below this value
GYRO_LO_THRES = -8  # AND above this value
DELTA_T = 0.12

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
        if smoothed_y > 0:      # up-direction fixer scalar
            smoothed_y *= 0.7
        if smoothed_z > 0:      # left-direction fixer scalar
            smoothed_z *= 0.9
        GYRO_Y.get()        # remove the first element from the queues
        GYRO_Z.get()
        if smoothed_y >= GYRO_LO_THRES and smoothed_y <= GYRO_HI_THRES: smoothed_y = 0
        if smoothed_z >= GYRO_LO_THRES and smoothed_z <= GYRO_HI_THRES: smoothed_z = 0
        return smoothed_y * DELTA_T, -1 * smoothed_z * DELTA_T
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
    return int(min(245, 0.9 * abs(channel)))

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

# Mother function
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

def get_correcting_scalar(CANVAS_WIDTH, CANVAS_HEIGHT, lasx, lasy):
    """
    Calculates the movement speed fixing scalars based on canvas dimensions and
    current location. Makes it easier to move towards the middle when at borders
    Returns the x-direction scalar and the y-direction scalar
    """
    BORDER_SPEED = 2    # the max movement scalar, reached at borders
    scalar_x = scalar_y = 1
    ratio_x = lasx / CANVAS_WIDTH
    ratio_y = lasy / CANVAS_HEIGHT
    if   ratio_x < 0.3: scalar_x = (1 - BORDER_SPEED) / 0.3 * ratio_x + BORDER_SPEED
    elif ratio_x > 0.7: scalar_x = (BORDER_SPEED - 1) / 0.3 * ratio_x + BORDER_SPEED - (BORDER_SPEED - 1) / 0.3
    if   ratio_y < 0.3: scalar_y = (1 - BORDER_SPEED) / 0.3 * ratio_y + BORDER_SPEED
    elif ratio_y > 0.7: scalar_y = (BORDER_SPEED - 1) / 0.3 * ratio_y + BORDER_SPEED - (BORDER_SPEED - 1) / 0.3
    return scalar_x, scalar_y
