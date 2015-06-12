__author__ = 'ankit'

import pygame as pg
import threading
from pygame.locals import *
from Tkinter import *
from ttk import Frame
from tkFileDialog import askopenfilename, askopenfile
import sys, os
if sys.platform == 'win32' and sys.getwindowsversion()[0] >=5:
    os.environ['SDL_VIDEODRIVER'] = 'windib'

class playar(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.filenm=None
        self.pack(fill=BOTH, expand=1)
        self.parent = parent
        self.initplayer()

    def initplayer(self):
        self.videoFrame = Frame(self, width=800, height=480)
        self.videoFrame.pack(side="top", fill="both", expand=True)
        self.buttonframe = Frame(self, padding="2 2 11 11")
        self.buttonframe.pack(side="bottom", fill="x", expand=True)

        self.selectbutton = Button(self.buttonframe, text="Select")
        self.selectbutton.grid(column=0, row=0, sticky=W)
        self.playbutton = Button(self.buttonframe, text="Play").grid(column=1, row=0, sticky=W)
        for child in self.buttonframe.winfo_children(): child.grid_configure(padx=5, pady=5)
        self.buttonframe.rowconfigure(0, weight=1)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)

    def setwh(self,w,h):
        self.videoFrame.configure(width=w, height=h)

    def quit(self):
        print "QUIT CALLED"
        pg.quit()
        self.destroy()

def pygameupdate(player, frame):
    global done
    clock = pg.time.Clock()
    pg.event.set_allowed((QUIT, KEYDOWN))
    while not done:
        frame.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                player.stop()
                done = True
        pg.display.update()
        clock.tick(60.0)
    frame.quit()


def pygamet(frame):
    global filenm
    pg.init()
    pg.mixer.quit()
    if filenm is None or filenm=="":
        filenm="cartest.mp4"
    player = pg.movie.Movie(filenm)
    w, h =[size * 3 for size in player.get_size()]
    screen = pg.display.set_mode((w+10, h+10))
    frame.setwh(w+5, h+5)
    player.set_display(screen, pg.Rect((5,5),(w,h)))
    player.play()
    pygameupdate(player,frame)

def filedlog(**opt):
    name = askopenfilename(**opt)
    return name

done = False
filenm = "MELT.MPG"

def stopeverything():
    global done
    done = True

if __name__ == "__main__":
    filenm = filedlog(filetypes = [("All Files","*.*"),
                                   ("MPEG Video Files","*.MPG;*.MPEG")])
    print filenm
    root = Tk()
    root.title("Video Player")
    root.wm_protocol("WM_DELETE_WINDOW", stopeverything)
    a = playar(root)
    os.environ['SDL_WINDOWID'] = str(a.videoFrame.winfo_id())
    pygamet(a)
    root.destroy()