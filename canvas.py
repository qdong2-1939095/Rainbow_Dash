from tkinter import *

canvas = None
app = None
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 720
def load_canvas():
    global canvas, app
    app = Tk()
    geo = str(CANVAS_WIDTH) + "x" + str(CANVAS_HEIGHT)
    app.geometry(geo)
    canvas = Canvas(app, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
    canvas.pack(pady=20)

lasx = CANVAS_WIDTH / 2
lasy = CANVAS_HEIGHT / 2

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb

def draw_line(x_offset, y_offset, r, g, b):
    global lasx, lasy
    canvas.create_line((lasx, lasy, x_offset, y_offset),
                      fill=_from_rgb((r, g, b)),
                      width=2)
    lasx, lasy = lasx + x_offset, lasy + y_offset
app.mainloop()