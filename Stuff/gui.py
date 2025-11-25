from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from time import localtime, strftime, time, sleep
from collections import defaultdict
from uuid import uuid4

import urllib.request
import urllib.parse
import os
import json

from constants import TESTING, URL, GOTHROUGH, PARTICIPATION_FEE
from common import change_keyboard_layout


class GUI(Tk):
    def __init__(self, frames, load = False):
        super().__init__()
        
        self.title("Experiment")
        self.config(bg = "white")
        windowed = TESTING or URL == "http://127.0.0.1:8000/"
        if windowed:
            #self.geometry("1920x1080")
            #self.geometry("1680x1050")
            self.geometry("1280x1024")
        self.attributes("-fullscreen", not windowed)
        self.attributes("-topmost", not windowed)
        self.overrideredirect(not windowed)
        self.protocol("WM_DELETE_WINDOW", lambda: self.closeFun())

        self.screenwidth = 1280 # 1680 # 1920 # adjust
        self.screenheight = 1024 # 1050 # 1080 # adjust

        os.chdir(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
        filepath = os.path.join(os.getcwd(), "Data")
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        
        writeTime = localtime()
        self.id = str(uuid4())
        self.outputfile = os.path.join("Data", strftime("%y_%m_%d_%H%M%S", writeTime) + "_" + self.id + ".txt")

        self.bind("<Escape>", self.closeFun)

        self.order = frames

        self.texts = defaultdict(str)
        self.status = defaultdict(str)
        self.status["logged"] = False
        self.status["reward"] = PARTICIPATION_FEE
        self.status["results"] = []

        self.count = -1

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

        if load and URL != "TEST":            
            if os.path.exists("temp.json"):
                ans = messagebox.askyesno(
                    message="Má se načíst započatý experiment?",
                    icon="question",
                    parent=self,
                    title="Pokračovat v experimentu?"
                )
                if ans:
                    with open('temp.json') as f:
                        data = json.load(f)            
                    message = urllib.parse.urlencode({"id": data["id"], "round": data["count"], "offer": "continue"})
                    message = message.encode('ascii')
                    with urllib.request.urlopen(URL, data = message) as f:
                        response = f.read().decode("utf-8")                
                    if response == "continue":
                        for key, value in data.items():
                            setattr(self, key, value)  
                    else:
                        load = False  
                else:
                    load = False
                self.focus_force()

        if TESTING:
            self.title("TEST " + self.id)
        else:
            try:
                change_keyboard_layout("00000405") # Change to Czech layout
            except Exception as e:
                print(f"Error changing keyboard layout: {e}")

        mode = "a" if load else "w"
        with open(self.outputfile, mode = mode, encoding = "utf-8") as self.file:
            self.nextFrame()
            self.after(100, self.frame.focus_force)
            self.mainloop()
            

    def destroy(self):
        self.file.close()
        if URL != "TEST":
            self.uploadResults()        
        super().destroy()


    def removeJson(self):
        try:
            if os.path.exists("temp.json"):
                os.remove("temp.json")
        except Exception as e:
            if TESTING:
                print("Could not remove temp.json:", e)


    def nextFrame(self):
        if not GOTHROUGH:
            self.removeJson()
            with open("temp.json", mode = "w") as f:
                json.dump({"id": self.id,
                        "outputfile": self.outputfile,
                        "texts": self.texts,
                        "status": self.status,
                        "count": self.count}, 
                        f)

        self.file.write("time: " + str(time()) + "\n")
        self.count += 1       
        if self.count >= len(self.order):
            if not GOTHROUGH:
                self.removeJson()
            self.destroy()
        else:
            nxt = self.order[self.count]
            if isinstance(nxt, tuple):
                self.frame = nxt[0](self, **nxt[1])
            else:
                self.frame = nxt(self)
            self.frame.grid(row = 0, column = 0, sticky = (N, S, E, W))     
            if self.status["logged"]:
                self.frame.sendData({'id': self.id, 'round': self.count, 'offer': "progress"}, pause = 0.01, trials = 5)

            if GOTHROUGH and GOTHROUGH != type(self.frame).__name__ and (type(GOTHROUGH) is not int or GOTHROUGH < self.count):
                self.update()
                sleep(0.5)
                self.frame.gothrough()
            elif hasattr(self.frame, "run"):
                self.update()
                self.frame.run()


    def closeFun(self, event = ""):
        if TESTING:
            self.destroy()
            return
        
        message = "Jste si jistí, že chcete studii předčasně ukončit? "
        ans = messagebox.askyesno(message = message, icon = "question", parent = self,
                                  title = "Ukončit studii?")
        if ans:
            self.destroy()


    def uploadResults(self):
        for i in range(20):
            # Set the URL of the Django app that handles file uploads
            url = URL + "results/"

            # Open the file and read its contents
            with open(self.outputfile, "rb") as f:
                file_contents = f.read()

            # Encode the file contents as multipart/form-data
            boundary = b"----WebKitFormBoundary7MA4YWxkTrZu0gW"
            data = b""
            data += b"--" + boundary + b"\r\n"
            filename = os.path.basename(self.outputfile)
            data += bytes('Content-Disposition: form-data; name="results"; filename="{}"\r\n'.format(filename), 'UTF-8')
            data += b"Content-Type: text/plain\r\n\r\n"
            data += file_contents + b"\r\n"
            data += b"--" + boundary + b"--\r\n"

            # Set the headers and data for the request
            headers = {
                "Content-Type": "multipart/form-data; boundary=" + boundary.decode(),
                "Content-Length": str(len(data)),
            }
            request_data = urllib.request.Request(url, data, headers)
            
            try:
                # Send the file to the Django app
                response = urllib.request.urlopen(request_data)
                # Print the response from the Django app
                if response.read().decode() == "ok":
                    break
            except Exception:
                sleep(0.5)