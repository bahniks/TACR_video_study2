from tkinter import *
from tkinter import ttk
import tkinter.font as tkfont
from collections import deque
from time import perf_counter, sleep
from math import ceil

import random
import os

from common import ExperimentFrame, InstructionsFrame, Question, Measure, read_all
from gui import GUI
from constants import TESTING, AUTOFILL


intro = "Označte, do jaké míry souhlasíte s následujícímí tvrzeními, na poskytnuté škále."

uppsIntro = """Přečtěte si prosím každé tvrzení a označte, nakolik s ním souhlasíte."""


class Questionnaire(ExperimentFrame):
    def __init__(self, root, words, question = "", labels = None, blocksize = 4, values = 7, text = True,
                 filetext = "", fontsize = 13, labelwidth = None, wraplength = 0, pady = 0, fixedlines = 0, randomize = False, perpage = 0, questionnaireHeight = "auto", labelFontsize = "auto"):
        super().__init__(root)

        self.fontsize = fontsize
        self.blocksize = blocksize
        self.values = values
        self.text = text
        self.fixedlines = fixedlines
        self.labelwidth = labelwidth
        self.wraplength = wraplength
        self.pady = pady
        self.question = question
        self.answers = labels
        self.perpage = perpage
        self.labelFontsize = labelFontsize if labelFontsize != "auto" else self.fontsize

        if filetext:
            self.file.write(filetext + "\n")

        if type(words) == str and os.path.exists(os.path.join(os.path.dirname(__file__), words)):
            self.allwords = read_all(os.path.join(os.path.dirname(__file__), words)).split("\n")
        else:
            self.allwords = words
        if randomize:
            random.shuffle(self.allwords)
        if perpage and len(self.allwords) > perpage:
            self.screen = 1                      
            self.words = self.allwords[:perpage]
        else:
            self.words = self.allwords

        self.buttons = {}
        self.variables = {}
        self.labels = {}

        self.frame = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.frame.grid(column = 1, row = 1, sticky = NSEW, pady = 10)
        self.createWidgets()
        if questionnaireHeight != "auto":
            self.filler = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white", height = questionnaireHeight, width = 1)
            self.filler.grid(column = 0, row = 1, sticky = NSEW)

        self.question = ttk.Label(self, text = self.question, background = "white", font = "helvetica 15")
        self.question.grid(column = 1, row = 0, sticky = S, pady = 10)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 2)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 2)
        self.rowconfigure(3, weight = 1)

    def createWidgets(self):
        maxwidth = max(map(len, self.words))

        for count, word in enumerate(self.words, 1):
            self.variables[word] = StringVar()
            if AUTOFILL:
                self.variables[word].set(random.randint(1, self.values))
            for i in range(1, self.values+1):
                if word not in self.buttons:
                    self.buttons[word] = {}
                valuetext = str(i) if self.text else ""
                self.buttons[word][i] = ttk.Radiobutton(self.frame, text = valuetext, value = i,
                                                        command = self.clicked,
                                                        variable = self.variables[word])
                self.buttons[word][i].grid(column = i+1, row = count + (count-1)//self.blocksize, padx = 15)

            if self.fixedlines:
                fillerlabel = ttk.Label(self.frame, text = "l" + "\nl"*int(self.fixedlines - 1), background = "white", foreground = "white", font = "helvetica {}".format(self.fontsize))
                fillerlabel.grid(column = 0, row = count + (count-1)//self.blocksize, pady = self.pady)

            self.labels[word] = ttk.Label(self.frame, text = word, background = "white",
                                          font = "helvetica {}".format(self.fontsize), justify = "left",
                                          width = maxwidth/1.2, wraplength = self.wraplength)
            self.labels[word].grid(column = 1, row = count + (count-1)//self.blocksize, padx = 15, sticky = W, pady = self.pady)
            if not count % self.blocksize:
                self.frame.rowconfigure(count + count//self.blocksize, weight = 1)

        avg_char_width = tkfont.Font(family="helvetica", size=self.fontsize).measure("s")
        if self.wraplength:
            fillerSize = min([int(ceil(maxwidth/(1+maxwidth/1000))), self.wraplength//avg_char_width])
        else:
            fillerSize = int(ceil(maxwidth/(1+maxwidth/1000)))
        fillerLabel = ttk.Label(self.frame, text = "s"*fillerSize, background = "white", font = "helvetica {}".format(self.fontsize+1), foreground = "white", justify = "left", width = maxwidth/1.2, wraplength = self.wraplength)
        fillerLabel.grid(column = 1, padx = 15, sticky = W, row = count + 1 + (count-1)//self.blocksize)

        self.texts = []
        if not self.answers:
            self.answers = [""]*self.values
        elif len(self.answers) != self.values:
            self.answers = [self.answers[0]] + [""]*(self.values - 2) + [self.answers[-1]]

        for count, label in enumerate(self.answers):
            self.texts.append(ttk.Label(self.frame, text = label, background = "white",
                                        font = "helvetica {}".format(self.labelFontsize), anchor = "center",
                                        justify = "center", wraplength = self.labelwidth * tkfont.Font(family="helvetica", size=self.labelFontsize, weight="normal").measure("0")))
            if self.labelwidth:
               self.texts[count]["width"] = self.labelwidth,
            self.texts[count].grid(column = count+2, row = 0, sticky = W, pady = 4, padx = 3)

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica {}".format(self.fontsize))

        ttk.Style().configure("TButton", font = "helvetica 15")
        self.next = ttk.Button(self, text = "Pokračovat", command = self.nextFun, state = "disabled")
        self.next.grid(column = 1, row = 2)

    def nextFun(self):
        if self.perpage and len(self.allwords) > self.screen * self.perpage:
            self.write()
            self.screen += 1
            self.words = self.allwords[(self.screen-1)*self.perpage:self.screen*self.perpage]
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.buttons = {}
            self.variables = {}
            self.labels = {}
            self.createWidgets()
            return
        return super().nextFun()

    def clicked(self):
        end = True
        for word in self.words:
            if not self.variables[word].get():
                end = False
            else:
                self.labels[word]["foreground"] = "grey"
        if end:
            self.next["state"] = "!disabled"

    def write(self):
        for word in self.words:
            self.file.write(self.id + "\t" + word + "\t" + self.variables[word].get() + "\n")

    def gothrough(self):
        for word in self.words:
            choice = random.randint(1, self.values)
            self.buttons[word][choice].invoke()
        self.update()
        sleep(0.5)
        self.next.invoke()





UPPS = (Questionnaire,
                {"words": "upps.txt",
                    "question": uppsIntro,
                    "labels": ["rozhodně nesouhlasím",
                                "spíše nesouhlasím",
                                "spíše souhlasím",
                                "rozhodně souhlasím"],
                    "values": 4,
                    "labelwidth": 11,
                    "text": False,
                    "fontsize": 12,
                    "blocksize": 8,
                    "wraplength": 750,
                    "filetext": "UPPS",
                    "fixedlines": 2,
                    "pady": 5})




if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([UPPS])