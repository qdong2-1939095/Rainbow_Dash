from tkinter import *

canvas = None

def load_canvas():
    global canvas
    app = Tk()
    app.geometry("1080x720")
    canvas = Canvas(app, width=1080, height=720, bg='white')
    canvas.pack(pady=20)

lasx = 540
lasy =  360

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
# app.mainloop()