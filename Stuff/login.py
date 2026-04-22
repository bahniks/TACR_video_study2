#! python3
# -*- coding: utf-8 -*- 

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import perf_counter, sleep
from collections import defaultdict

import random
import os
import urllib.request
import urllib.parse

from common import InstructionsFrame
from gui import GUI
from constants import TESTING, URL






class Login(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "Počkejte na spuštění experimentu", height = 3, font = 15, width = 45, proceed = False)

        self.progressBar = ttk.Progressbar(self, orient = HORIZONTAL, length = 400, mode = 'indeterminate')
        self.progressBar.grid(row = 2, column = 1, sticky = N)

    def login(self):       
        count = 0
        while True:
            self.update()
            if count % 50 == 0:            
                data = urllib.parse.urlencode({'id': self.root.id, 'round': 0, 'offer': "login"})
                data = data.encode('ascii')
                if URL == "TEST":               
                    response = "start"
                else:
                    response = ""
                    try:
                        with urllib.request.urlopen(URL, data = data) as f:
                            response = f.read().decode("utf-8") 
                        self.root.status["logged"] = True
                    except Exception:
                        self.changeText("Server nedostupný")                    
                if "start" in response:
                    self.update_intros()
                    self.progressBar.stop()
                    self.write()
                    self.nextFun()                      
                    break
            count += 1                  
            sleep(0.1)        

    def run(self):
        self.progressBar.start()
        self.login()

    def update_intros(self):
        self.root.status["condition"] = random.choice(["nudge", "boost", "control"])
        self.root.status["videoNumber"] = 1
        self.root.status["distractions1"] = ["chat", "game", "tiktok", "control"]
        self.root.status["distractions2"] = ["chat", "game", "tiktok", "control"]
        random.shuffle(self.root.status["distractions1"])
        random.shuffle(self.root.status["distractions2"])        
        self.root.status["distractions"] = self.root.status["distractions1"] + self.root.status["distractions2"]             
        self.root.status["chat_order"] = ["chatA.txt", "chatB.txt"]
        random.shuffle(self.root.status["chat_order"])

    def write(self):
        self.file.write("Login" + "\n")
        self.file.write(self.id + "\t" + self.root.status["condition"] + "\t" + "\t".join(self.root.status["distractions"]) + "\n\n")        

    def gothrough(self):
        self.run()