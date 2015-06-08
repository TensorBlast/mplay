__author__ = 'ankit'

from Tkinter import *
from ttk import Frame, Button, Style
from multiprocessing import Process, Queue
from Queue import Empty
import numpy as np
import cv2
from PIL import Image, ImageTk


class mplaywin():
    def quit_(self, root, process):
        process.join()
        root.destroy()

    def __init__(self):
        root = Tk()
        root.title("mplay Video Player")

        # mainframe = ttk.Frame(root, padding="3 3 12 12")
        # mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        # mainframe.columnconfigure(0, weight=1)
        # mainframe.rowconfigure(0, weight=1)
        #
        # self.feet = StringVar()
        # self.met = StringVar()
        #
        # feet_enter = ttk.Entry(mainframe, width=7, textvariable=self.feet)
        # feet_enter.grid(column=2, row=1, sticky=(W, E))
        #
        # ttk.Label(mainframe, textvariable=self.met).grid(column=2, row=2, sticky=(W, E))
        # ttk.Button(mainframe, text="Calculate", command=self.calc).grid(column=4, row=4, sticky=W)
        #
        # ttk.Label(mainframe, text="Feet: ").grid(column=1, row=1, sticky=E)
        # ttk.Label(mainframe, text="Meters: ").grid(column=1, row=2, sticky=E)
        #
        # for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
        #
        # feet_enter.focus()
        # root.bind('<Return>', self.calc)
        #
        # root.mainloop()
        root.configure(width=840, height=500)
        self.mainframe = Frame(root, padding="3 3 12 12")
        self.mainframe.pack(side="top", fill="both", expand=True)
        self.mainframe.configure(width=800, height=480)

        self.buttonframe = Frame(root, padding="2 2 11 11")
        self.buttonframe.pack(side="bottom", fill="both", expand=True)

        self.selectbutton = Button(self.buttonframe, text="Select").grid(column=0, row=0, sticky=W)
        self.playbutton = Button(self.buttonframe, text="Play").grid(column=1, row=0, sticky=W)
        for child in self.buttonframe.winfo_children(): child.grid_configure(padx=5, pady=5)
        self.buttonframe.rowconfigure(0, weight=1)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)

        self.image_label = Label(self.mainframe)
        self.image_label.pack()
        proc, q = initializeplayback()
        root.after(0, func=lambda: update_all(root, self.image_label, q))
        root.mainloop()
        proc.terminate()

    def calc(self, *args):
        try:
            val = float(self.feet.get())
            self.met.set((0.3048 * val * 10000.0 + 0.5) / 10000.0)
        except ValueError:
            pass

def update_all(root, image_label, qu):
    update_image(root, qu, image_label)
    root.after(0, func=lambda: update_all(root, image_label, qu))


def update_image(root, queue, image_label):
    frame = queue.get()
    im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    a = Image.fromarray(im)
    b = ImageTk.PhotoImage(image=a)
    image_label.configure(image=b)
    image_label._image_cache = b
    root.update()


def image_capture(queue):
    vidFile = cv2.VideoCapture("lotgh.mkv")
    while True:
        try:
            flag, frame = vidFile.read()
            if flag == 0:
                break
            queue.put(frame)
        except:
            continue


def initializeplayback():
    queue = Queue()
    print 'initializeplayback called...'
    proc = Process(target=image_capture, args=(queue,))
    proc.start()
    return proc, queue




if __name__ == "__main__":
    test = mplaywin()