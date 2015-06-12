__author__ = 'ankit'

from Tkinter import *
from ttk import Frame
from tkFileDialog import askopenfilename, askopenfile
from tkMessageBox import showerror, showinfo
import sys, os
from subprocess import *


class mainframe(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.filenm=None
        self.pack(fill=BOTH, expand=1)
        self.parent = parent
        self.initplayer()
        self.player_process = None

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

        self.selectbutton.configure(command = self.fileopen)
        self.videoFrame.bind("<Button-1>",self.playpause)

    def fileopen(self):
        self.filenm = self.filenm=askopenfilename(filetypes=[("Supported Files","*.mp4;*.mkv;*.mpg;*.avi")])
        self.play()

    def play(self):
        if self.filenm is not None and self.filenm != "":
            winid = self.videoFrame.winfo_id()
            if self.player_process is not None:
                self.player_process.kill()
            try:
                self.player_process = Popen(["mpv","--wid",str(winid),self.filenm],stdin=PIPE)
            except:
                showerror("Error","".join(["Couldn't play video:\n",str(sys.exc_info()[1]),str(sys.exc_info()[2])]))

    def playpause(self, event):
        if self.player_process is None:
            return
        self.command_player(0x0201)

    def setwh(self,w,h):
        self.videoFrame.configure(width=w, height=h)

    def quit(self):
        print "QUIT CALLED"
        self.destroy()

    def command_player(self, comd):
        if self.player_process is not None:
            print 'Attempting to write %s to mpv' % str(comd)
            comd = str(comd)
            self.player_process.stdin.write(comd+'\n')

    def stop(self):
        self.player_process.kill()
        self.player_process = None


primary = None

def stopeverything():
    global primary
    primary.stop()
    primary.destroy()
    root.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title('MPV X Video Player')
    root.wm_protocol("WM_DELETE_WINDOW", stopeverything)
    primary = mainframe(root)
    root.mainloop()