from tkinter import *
from tkinter import ttk

import os

from common import ExperimentFrame
from gui import GUI


comments = """
Zde je prostor pro Vaše komentáře či připomínky ohledně průběhu celé studie.
"""

class Comments(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        self.file.write("Comments\n")

        self.comment = CommentFrame(self, comments)
        self.comment.grid(row = 1, column = 1)

        ttk.Style().configure("TButton", font = "helvetica 15")
        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun)
        self.next.grid(column = 1, row = 2)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)


    def write(self):
        self.comment.write()      
                      
        

class CommentFrame(Canvas):
    def __init__(self, root, name):
        super().__init__(root)

        self["background"] = "white"
        self["highlightbackground"] = "white"
        self["highlightcolor"] = "white"

        self.root = root
        self.name = name

        self.label = ttk.Label(self, text = name, background = "white", font = "helvetica 15", anchor = "center")
        self.label.grid(column = 0, row = 0, pady = 5, sticky = EW)

        self.text = Text(self, height = 12, width = 80, relief = "solid", font = "helvetica 15")
        self.text.grid(column = 0, row = 1)


    def write(self):
        content = self.text.get("1.0", "end")
        self.root.file.write(self.root.id + "\t" + content.replace("\n", "  ").replace("\t", " ") + "\n")



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Comments])
