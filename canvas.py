from tkinter import *
app = Tk()
app.geometry("1080x720")
canvas = Canvas(app, width=1080, height=720, bg='white')
canvas.pack(pady=20)
# canvas = Canvas(app, bg='red')
# canvas.pack(anchor='nw', fill='both', expand=1)

def get_x_and_y(event):
    global lasx, lasy
    lasx, lasy = event.x, event.y

def _from_rgb(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    return "#%02x%02x%02x" % rgb  

def draw_smth(event):
    global lasx, lasy
    canvas.create_line((lasx, lasy, event.x, event.y),
                      fill=_from_rgb((250, 200, 200)),
                      width=2)
    lasx, lasy = event.x, event.y

canvas.bind("<Button-1>", get_x_and_y)
canvas.bind("<B1-Motion>", draw_smth)
app.mainloop()