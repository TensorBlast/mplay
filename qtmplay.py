__author__ = 'ankit'

import pygame as pg
from pygame.locals import *
from Tkinter import *
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

        os.environ['SDL_WINDOWID'] = str(self.videoFrame.winfo_id())
        pg.init()
        pg.mixer.quit()
        self.filenm="MELT.MPG"
        if self.filenm is None or self.filenm=="":
            self.filenm="cartest.mp4"
        self.player = pg.movie.Movie(self.filenm)
        w, h =[size * 3 for size in self.player.get_size()]
        screen = pg.display.set_mode((w+10, h+10))
        self.player.set_display(screen, pg.Rect((5,5),(w,h)))
        self.videoFrame.configure(width=w+10, height=h+10)
        self.player.play()
        self.clock = pg.time.Clock()
        self.done = False
        pg.event.set_allowed((QUIT, KEYDOWN))
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.player.stop()
                    self.done = True
            screen.blit(screen,(0,0))
            pg.display.update()
            self.update()
            self.clock.tick(60.0)
        pg.quit()

    def quit(self):
        pg.quit()
        Frame.quit()


if __name__ == "__main__":
    root = Tk()
    root.title("Video Player")
    a = playar(root)
    root.mainloop()
    a.quit()
    root.quit()