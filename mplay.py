__author__ = 'ankit'

from tkinter import *
from tkinter import ttk


class mplaywin:
    def __init__(self):
        root = Tk()
        root.title("mplay Video Player")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        self.feet = StringVar()
        self.met = StringVar()

        feet_enter = ttk.Entry(mainframe, width=7, textvariable=self.feet)
        feet_enter.grid(column=2, row=1, sticky=(W, E))

        ttk.Label(mainframe, textvariable=self.met).grid(column=2, row=2, sticky=(W, E))
        ttk.Button(mainframe, text="Calculate", command=self.calc).grid(column=4, row=4, sticky=W)

        ttk.Label(mainframe, text="Feet: ").grid(column=1, row=1, sticky=E)
        ttk.Label(mainframe, text="Meters: ").grid(column=1, row=2, sticky=E)

        for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

        feet_enter.focus()
        root.bind('<Return>', self.calc)

        root.mainloop()

    def calc(self, *args):
        try:
            val = float(self.feet.get())
            self.met.set((0.3048 * val * 10000.0 + 0.5) / 10000.0)
        except ValueError:
            pass


if __name__ == "__main__":
    test = mplaywin()