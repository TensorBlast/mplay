__author__ = 'ankit'

from Tkinter import *
from ttk import Frame
from tkFileDialog import askopenfilename, askopenfile
from tkMessageBox import showerror, showinfo
from subprocess import *
from threading import Thread
from Queue import Queue, Empty, LifoQueue
import os, sys

class mainframe(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.filenm=None
        self.streamnm = None
        self.pack(fill=BOTH, expand=1)
        self.parent = parent
        self.initplayer()
        self.player_process = None
        self.fstate = False
        self.paused = True
        self.trackmouse = True
        self.stdout_thread = None
        self.stream = False
        self.q = LifoQueue()

    def initplayer(self):
        self.parentframe = Frame(self)
        self.parentframe.pack(fill=BOTH, expand=True)
        self.videoFrame = Frame(self.parentframe, width=800, height=480)
        self.videoFrame.pack(side="top", fill="both", expand=True)
        self.buttonframe = Frame(self.parentframe, padding="2 2 1 1")
        self.buttonframe.pack(side="bottom", fill="x", expand=False)

        self.seekbar = Scale(self.buttonframe, from_= 0, to=100, orient=HORIZONTAL)
        self.seekbar.grid(column=0, columnspan=4, row=0, sticky=[N, E, S, W])

        self.selectbutton = Button(self.buttonframe, text="Select File")
        self.selectbutton.grid(column=0, row=1, sticky=[E,W])
        self.streambutton = Button(self.buttonframe, text="Open HTTP", command=self.streamopen)
        self.streambutton.grid(column=1, row=1, sticky=[E,W])
        self.playbutton = Button(self.buttonframe, text="Play")
        self.playbutton.config(command=self.playpause)
        self.playbutton.grid(column=2, row=1, sticky=[E,W])
        self.fullscreenbutton = Button(self.buttonframe, text="Fullscreen", command=self.togglefullscreen)
        self.fullscreenbutton.grid(column=3, row=1, sticky=[E,W])
        for child in self.buttonframe.winfo_children(): child.grid_configure(padx=5, pady=5)
        self.buttonframe.rowconfigure(0, weight=1)
        self.buttonframe.rowconfigure(1, weight=1)
        self.buttonframe.columnconfigure(0, weight=1)
        self.buttonframe.columnconfigure(1, weight=1)
        self.buttonframe.columnconfigure(2, weight=1)
        self.buttonframe.columnconfigure(3, weight=1)

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
            self.fullscreenbutton.config(text="Exit Fullscreen")
            self.buttonframe.pack_forget()
            self.videoFrame.config(cursor="none")
        else:
            self.fullscreenbutton.config(text="Fullscreen")
            self.buttonframe.pack(side="bottom", fill="x", expand=False)
            self.videoFrame.after(5000, self.cursorhandler)

    def fileopen(self):
        self.filenm = askopenfilename(filetypes=[("Supported Files","*.mp4;*.mkv;*.mpg;*.avi;*.mov"),("All Files","*.*")])
        self.stream = False
        self.play()

    def streamopen(self):
        self.streamnm = Dlog(self.parent)
        if self.streamnm.result is not None:
            s = str(self.streamnm)
        else:
            return
        if s.startswith('http'):
            self.stream = True
            self.play()
        else:
            self.stream = False
            showerror("Error","Incorrect Entry")

    def play(self):
        if self.filenm is not None and self.filenm != "":
            winid = self.videoFrame.winfo_id()
            if self.mplayer_isrunning():
                self.stop()
            try:
                self.paused = False
                self.playbutton.configure(text="Pause")
                if not self.stream:
                    self.player_process = Popen(["mplayer","-fs","-slave","-quiet","-wid",str(winid),self.filenm],stdin=PIPE, stdout=PIPE)
                else:
                    self.player_process = Popen(["mplayer","-fs","-slave","-quiet","-wid",str(winid),self.streamnm], stdin=PIPE, stdout=PIPE)
                self.stdout_thread = Thread(target=self.enqueue_pipe, args=(self.player_process.stdout, self.q))
                self.stdout_thread.daemon = True
                self.stdout_thread.start()
                # self.seekthread = Thread(target=self.seekbar_updater, args=())
                # self.seekthread.daemon = True
                #self.seekthread.start()
            except:
                showerror("Error","".join(["Couldn't play video:\n",str(sys.exc_info()[1]),str(sys.exc_info()[2])]))

    def getvidtime(self):
        pproc = Popen(["mplayer","-really-quiet","-nosound","-vo","null","-identify",self.filenm], stdout=PIPE)
        pproc.stdout.flush()
        print pproc.stdout.read()
        pproc.kill()

    def playpause(self, event=None):
        if self.player_process is None:
            return
        self.paused = not self.paused
        if self.paused:
            print "VIDEO IS PAUSED /B/RO"
            self.playbutton.configure(text="Play")
        else:
            self.playbutton.configure(text="Pause")
        self.command_player("pause")
        print self.readpipe()

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
        if self.mplayer_isrunning():
            try:
                self.player_process.stdin.write("%s\r\n"%comd)
                self.player_process.stdin.flush()
            except :
                showerror("Error","Error passing command to mplayer\n%s"%sys.exc_info()[1])

    def enqueue_pipe(self, out, q):
        print 'enq'
        for line in iter(out.readline, b''):
            q.put(line)
        out.close()

    def seekbar_updater(self):
        pos = self.getvidtime()
        self.seekbar.set(int(pos))

    def readpipe(self):
        # print 'Trying to read PIPE...'
        line = ""
        try:
            line = self.q.get_nowait()
        except Empty:
            print "Empty PIPE"
        else:
            return line

    def stop(self):
        if self.mplayer_isrunning():
            self.player_process.stdin.write("quit\n")
            self.player_process.stdin.flush()
            print self.player_process.stdout.read()
        self.player_process = None


primary = None

class Dlog:

    def __init__(self, root):
        self.frm = top = Toplevel(root)
        top.protocol("WM_DELETE_WINDOW", self.endtask)
        top.title("Configure Stream")

        self.lbl = Label(top, text="Enter URL of stream\nEg:192.168.0.1:8080").pack()
        self.e = Entry(top)
        self.e.pack(padx=5, pady=5)

        self.result = ""
        b = Button(top, command=self.enter, text="OK").pack(pady=5)
        top.wait_window(top)

    def enter(self):
        self.result = self.e.get()
        self.frm.destroy()

    def endtask(self):
        self.result = None
        self.frm.destroy()

    def __str__(self):
        return self.result


def stopeverything():
    global primary
    primary.stop()
    primary.destroy()
    root.destroy()

if __name__ == "__main__":
    root = Tk()
    root.title('MPV X Video Player')
    root.protocol("WM_DELETE_WINDOW", stopeverything)
    primary = mainframe(root)
    root.mainloop()