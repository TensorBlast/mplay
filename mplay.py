__author__ = 'ankit'

from Tkinter import *
from ttk import Frame
from tkFileDialog import askopenfilename
from tkMessageBox import showerror
from subprocess import *
from threading import Thread, Timer
from Queue import Queue, Empty, LifoQueue
import os, sys, tempfile
import itertools

fifofilename = "fifotmp"
class mainframe(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.filenm=None
        self.streamnm = None
        self.pack(fill=BOTH, expand=1)
        self.parent = parent
        self.initplayer()
        self.player_process = None
        self.seekthread = None
        self.fstate = False
        self.paused = True
        self.trackmouse = True
        self.stdout_thread = None
        self.stream = False
        self.inhibit_slider_trigger = False
        self.q = LifoQueue()
        self.currtime = 0
        self.endtime = -1

    def initplayer(self):
        self.parentframe = Frame(self)
        self.parentframe.pack(fill=BOTH, expand=True)
        self.videoFrame = Frame(self.parentframe, width=800, height=480)
        self.videoFrame.pack(side="top", fill="both", expand=True)
        self.buttonframe = Frame(self.parentframe, padding="2 2 1 1")
        self.buttonframe.pack(side="bottom", fill="x", expand=False)

        self.seekbar = Scale(self.buttonframe, from_= 0, to=100, orient=HORIZONTAL)
        self.seekbar.grid(column=0, columnspan=4, row=0, sticky=[N, E, S, W])
        self.seekbar.configure(command=self.seeked)

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
            if windowy - 30 <= y:
                if self.fstate:
                    self.buttonframe.pack(side="bottom", fill="x", expand=False)
                    self.trackmouse = False
                    self.parent.after(5000, self.mousetracker)
                self.inhibit_slider_trigger = False
            elif self.fstate:
                self.buttonframe.pack_forget()
                self.inhibit_slider_trigger = True
            else:
                self.inhibit_slider_trigger = True

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
        global fifofilename
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
                self.emptypipe()
                self.seekthread = Thread(target=self.seekbar_setup, args=())
                self.seekthread.daemon = True
                self.seekthread.start()
            except:
                showerror("Error","".join(["Couldn't play video:\n",str(sys.exc_info()[:])]))

    def getvidtime(self):
        if self.mplayer_isrunning():
            self.command_player("get_time_length")
            output = self.readpipe()
            while "ANS_LENGTH" not in output:
                output = self.readpipe()
            if "ANS_LENGTH" in output:
                return output.split('ANS_LENGTH=')[1]
            else:
                return 0

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
        global fifofilename
        if self.mplayer_isrunning():
            try:
                self.player_process.stdin.flush()
                self.player_process.stdin.write("\r\n%s\r\n"%comd)
                # for _ in itertools.repeat(None,8192):
                #     self.player_process.stdin.write("\n")
                self.player_process.stdin.flush()
            except:
                showerror("Error","Error passing command to mplayer\n%s"%sys.exc_info()[1])

    def enqueue_pipe(self, out, q):
        print 'Working on reading mplayer pipe output...'
        for line in iter(out.readline, b''):
            q.put(line)
        out.close()

    def seekbar_setup(self):
        pos = '0'
        trial = 0
        while float(pos)<1:
            trial += 1
            pos = self.getvidtime()
        self.seekbar.config(to=int(float(pos)))
        self.endtime = int(float(pos))
        Timer(1, self.seekbar_updater).start()

    def seekbar_updater(self):
        if not self.paused and self.inhibit_slider_trigger:
            self.currtime += 1
            self.seekbar.set(self.currtime)
        else:
            self.currtime = self.seekbar.get()
        Timer(1, self.seekbar_updater).start()

    def seeked(self,e):
        pos = self.seekbar.get()
        print "We changed pos to :%d"% pos

        x, y = self.parent.winfo_pointerx(), self.parent.winfo_pointery()
        windowx, windowy = self.parent.winfo_width(), self.parent.winfo_height()
        if not self.inhibit_slider_trigger and windowy - 30 <= y:
            self.command_player("seek %d 2"%pos)
            if self.paused:
                self.command_player("pause")

    def startmousetrack(self):
        self.trackmouse = True

    def readpipe(self):
        line = ""
        try:
            line = self.q.get_nowait()
        except Empty:
            print "Empty PIPE"
        finally:
            return line

    def emptypipe(self):
        str = ''
        try:
            while not self.q.empty():
                str += self.q.get_nowait()
        except Empty:
            print "Empty Pipe"
        finally:
            return str

    def stop(self):
        if self.mplayer_isrunning():
            self.player_process.stdin.write("quit\n")
            self.player_process.stdin.flush()
            print self.emptypipe()
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