#! python3
from time import sleep
from tkinter import *
from tkinter import ttk

import os
import random

from time import sleep
from math import ceil

from common import InstructionsFrame
from gui import GUI


intro = "Uveďte své demografické údaje."


class Demographics(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = intro, width = 50, height = 1, savedata = True)
        self.text.grid(row = 0, column = 1, columnspan = 4, sticky = E)
       
        self.sex = StringVar()
        self.language = StringVar()
        self.age = StringVar()
        self.student = StringVar()
        self.field = StringVar()
        self.field.set("Nestuduji VŠ")

        self.lab1 = ttk.Label(self, text = "Pohlaví:", background = "white",
                              font = "helvetica 15")
        self.lab1.grid(column = 1, row = 1, pady = 2, sticky = W, padx = 2)
        self.lab2 = ttk.Label(self, text = "Věk:", background = "white",
                              font = "helvetica 15")
        self.lab2.grid(column = 1, row = 2, pady = 2, sticky = W, padx = 2)        
        self.lab3 = ttk.Label(self, text = "Mateřský jazyk:  ", background = "white",
                              font = "helvetica 15")
        self.lab3.grid(column = 1, row = 3, pady = 2, sticky = W, padx = 2)
        self.lab5 = ttk.Label(self, text = "Studujete VŠ?  ", background = "white",
                              font = "helvetica 15")
        self.lab5.grid(column = 1, row = 5, pady = 2, sticky = W, padx = 2)
        self.lab6 = ttk.Label(self, text = "Pokud ano, jaký obor? ", background = "white",
                              font = "helvetica 15")
        self.lab6.grid(column = 1, row = 6, pady = 2, sticky = W, padx = 2)
        
        self.male = ttk.Radiobutton(self, text = "muž", variable = self.sex, value = "male",
                                    command = self.checkAllFilled)
        self.female = ttk.Radiobutton(self, text = "žena", variable = self.sex,
                                      value = "female", command = self.checkAllFilled)
        self.otherSex = ttk.Radiobutton(self, text = "jiné", variable = self.sex,
                                      value = "other", command = self.checkAllFilled)

        self.czech = ttk.Radiobutton(self, text = "český", variable = self.language,
                                     value = "czech", command = self.checkAllFilled)
        self.slovak = ttk.Radiobutton(self, text = "slovenský", variable = self.language,
                                     value = "slovak", command = self.checkAllFilled)
        self.other = ttk.Radiobutton(self, text = "jiný", variable = self.language,
                                     value = "other", command = self.checkAllFilled)

        self.yes = ttk.Radiobutton(self, text = "ano", variable = self.student,
                                     value = "student", command = self.checkAllFilled)
        self.no = ttk.Radiobutton(self, text = "ne", variable = self.student,
                                    value = "nostudent", command = self.checkAllFilled)

        ttk.Style().configure("TRadiobutton", background = "white", font = "helvetica 15")
        ttk.Style().configure("TButton", font = "helvetica 15")

        self.ageCB = ttk.Combobox(self, textvariable = self.age, width = 6, font = "helvetica 15",
                                  state = "readonly")
        self.ageCB["values"] = tuple([""] + [str(i) for i in range(18, 80)])
        self.ageCB.bind("<<ComboboxSelected>>", lambda e: self.checkAllFilled())

        self.fieldCB = ttk.Combobox(self, textvariable = self.field, width = 25,
                                    font = "helvetica 15", state = "readonly")
        self.fieldCB["values"] = ["Nestuduji VŠ",
                                  "Ekonomie / management",
                                  "Jazyky / mezinárodní studia",
                                  "Kultura / umění",
                                  "Medicína / farmacie",
                                  "Právo / veřejná správa",
                                  "Přírodní vědy",
                                  "Technika / informatika",
                                  "Učitelství / sport",
                                  "Zemědělství / veterina",
                                  "Humanitní / společenské vědy",
                                  "Jiné"]
        self.fieldCB.bind("<<ComboboxSelected>>", lambda e: self.checkAllFilled())

        self.male.grid(column = 2, row = 1, pady = 7, padx = 7, sticky = W)
        self.female.grid(column = 3, row = 1, pady = 7, padx = 7, sticky = W)
        self.otherSex.grid(column = 4, row = 1, pady = 7, padx = 45, sticky = W)
        self.czech.grid(column = 2, row = 3, pady = 7, padx = 7, sticky = W)
        self.slovak.grid(column = 3, row = 3, pady = 7, padx = 7, sticky = W)
        self.other.grid(column = 4, row = 3, pady = 7, padx = 45, sticky = W)
        self.ageCB.grid(column = 2, row = 2, pady = 7, padx = 7, sticky = W)
        self.yes.grid(column = 2, row = 5, pady = 7, padx = 7, sticky = W)
        self.no.grid(column = 3, row = 5, pady = 7, padx = 7, sticky = W)
        self.fieldCB.grid(column = 2, columnspan = 3, row = 6, pady = 7, padx = 7, sticky = W)

        self.columnconfigure(5, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 0)
        self.rowconfigure(0, weight = 1)
        for i in range(1,7):
            self.rowconfigure(i, weight = 0)
        self.rowconfigure(7, weight = 1)

        self.next.grid(row = 7, column = 2, pady = 15)
        self.next["command"] = self.nextFun
        self.next["state"] = "disabled"


    def checkAllFilled(self, _ = None):
        if all([v.get() for v in [self.language, self.age, self.sex, self.field, self.student]]):
            self.next["state"] = "!disabled"


    def write(self):
        self.file.write("Demographics\n")
        self.file.write("\t".join([self.id, self.sex.get(), self.age.get(), self.language.get(),
                                   self.student.get(), self.field.get()]) + "\n\n")
        

    def gothrough(self):
        if random.random() < 0.5:
            self.male.invoke()
        else:
            self.female.invoke()
        age_choice = random.randint(18, 79)
        self.ageCB.set(str(age_choice))
        self.fieldCB.set(random.choice(self.fieldCB["values"][1:]))
        if random.random() < 0.8:
            self.czech.invoke()
        else:
            self.slovak.invoke()        
        if random.random() < 0.6:
            self.yes.invoke()
        else:
            self.no.invoke()
        sleep(0.5)
        self.update()
        self.next.invoke()  


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Demographics])
