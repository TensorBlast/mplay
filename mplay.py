__author__ = 'ankit'

from Tkinter import *
from ttk import Frame
from tkFileDialog import askopenfilename, askopenfile
from tkMessageBox import showerror, showinfo
from subprocess import *
import time

class mainframe(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.filenm=None
        self.pack(fill=BOTH, expand=1)
        self.parent = parent
        self.initplayer()
        self.player_process = None
        self.fstate = False
        self.paused = True
        self.trackmouse = True

    def initplayer(self):
        self.parentframe = Frame(self)
        self.parentframe.pack(fill=BOTH, expand=True)
        self.videoFrame = Frame(self.parentframe, width=800, height=480)
        self.videoFrame.pack(side="top", fill="both", expand=True)
        self.buttonframe = Frame(self.parentframe, padding="2 2 1 1")
        self.buttonframe.pack(side="bottom", fill="x", expand=False)

        self.selectbutton = Button(self.buttonframe, text="Select")
        self.selectbutton.grid(column=0, row=0, sticky=[E,W])
        self.playbutton = Button(self.buttonframe, text="Play")
        self.playbutton.config(command=self.playpause)
        self.playbutton.grid(column=1, row=0, sticky=[E,W])
        self.fullscreenbutton = Button(self.buttonframe, text="Fullscreen", command=self.togglefullscreen)
        self.fullscreenbutton.grid(column=2, row=0, sticky=[E,W])
        for child in self.buttonframe.winfo_children(): child.grid_configure(padx=5, pady=5)
        self.buttonframe.rowconfigure(0, weight=1)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)
        self.buttonframe.columnconfigure(2, weight=1)

        self.selectbutton.configure(command=self.fileopen)
        self.videoFrame.bind("<Button-1>",self.playpause)
        self.parent.bind("<F11>", self.togglefullscreen)
        self.parent.bind("<Motion>",self.mouseops)

    def mouseops(self,event=None):
        self.videoFrame.config(cursor="")
        self.videoFrame.after(5000,self.cursorhandler)
        if self.trackmouse:
            x, y = self.parent.winfo_pointerx(), self.parent.winfo_pointery()
            windowx, windowy = self.parent.winfo_width(), self.parent.winfo_height()
            if self.fstate and (windowy - 30 <= y):
                self.buttonframe.pack(side="bottom", fill="x", expand=False)
                self.trackmouse = False
                self.parent.after(5000, self.mousetracker)
            elif self.fstate:
                self.buttonframe.pack_forget()

    def mousetracker(self):
        print 'Mouse Tracker'
        self.trackmouse = True
        self.videoFrame.after(0,self.mouseops)

    def cursorhandler(self):
        self.videoFrame.config(cursor="none")

    def togglefullscreen(self, event=None):
        self.fstate = not self.fstate
        self.parent.attributes("-fullscreen",self.fstate)
        if self.fstate:
            self.buttonframe.pack_forget()
            self.videoFrame.config(cursor="none")
        else:
            self.buttonframe.pack(side="bottom", fill="x", expand=False)
            self.videoFrame.after(5000, self.cursorhandler)

    def fileopen(self):
        self.filenm = self.filenm=askopenfilename(filetypes=[("Supported Files","*.mp4;*.mkv;*.mpg;*.avi;*.mov")])
        self.play()

    def play(self):
        if self.filenm is not None and self.filenm != "":
            winid = self.videoFrame.winfo_id()
            if self.mplayer_isrunning():
                self.stop()
            try:
                self.paused = False
                self.playbutton.configure(text="Pause")
                self.player_process = Popen(["mplayer","-fs","-slave","-quiet","-wid",str(winid),self.filenm],stdin=PIPE, stdout=PIPE)
            except:
                showerror("Error","".join(["Couldn't play video:\n",str(sys.exc_info()[1]),str(sys.exc_info()[2])]))

    def playpause(self, event=None):
        if self.player_process is None:
            return
        self.paused = not self.paused
        if self.paused:
            self.playbutton.configure(text="Play")
        else:
            self.playbutton.configure(text="Pause")
        self.command_player("pause")

    def setwh(self,w,h):
        self.videoFrame.configure(width=w, height=h)

    def quit(self):
        print "QUIT CALLED"
        self.destroy()

    def mplayer_isrunning(self):
        if self.player_process is not None:
            return (self.player_process.poll() is None)
        else:
            return False

    def command_player(self, comd):
        if comd == "pause" and self.mplayer_isrunning():
            try:
                self.player_process.stdin.write("pause\n")
                self.player_process.stdin.flush()
            except :
                showerror("Error","Error passing command to mplayer\n%s"%sys.exc_info()[1])

    def stop(self):
        if self.mplayer_isrunning():
            self.player_process.stdin.write("quit\n")
            self.player_process.stdin.flush()
            print self.player_process.stdout.read()
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