#! python3

from tkinter import *
from tkinter import ttk

import os
import vlc
import random

from common import ExperimentFrame, Measure, InstructionsFrame, InstructionsAndUnderstanding
from questionnaire import Questionnaire
from gui import GUI
from login import Login
from constants import LIMIT, TESTING
from chat import Chat
from tiktok import TikTok
from game import Game



imiInstructions = """Nyní Vás prosíme o hodnocení zhlédnutého videa. 
U každého z následujících tvrzení uveďte, nakolik je pro vás pravdivé."""

imiInstructions2 = """Skvělé! Dokončili jste všech 5 videí. Můžete si sundat sluchátka, nebudete je již potřebovat.

Nyní Vás prosíme o hodnocení této série videí.
U každého z následujících tvrzení uveďte, nakolik je pro vás pravdivé.
"""

imiScale = ["zcela nepravdivé", "spíše nepravdivé", "do jisté míry pravdivé", "spíše pravdivé", "zcela pravdivé"]


attInstructions = """Zhodnoťte svou pozornost během právě zhlédnutého videa. 
U každé otázky vyberte na uvedené škále možnost, která nejlépe odpovídá Vaší zkušenosti."""

attQ1 = "Jak moc jste se soustředili na výukové video během jeho přehrávání?"
attQ2 = "Do jaké míry vaše pozornost odbíhala od videa?"

attScale = ["vůbec ne", "trochu", "středně", "hodně", "velmi hodně"]


quizInstructions1 = """
Nyní odpovězte na následující otázky týkající se obsahu právě zhlédnutého videa na Prokletí znalosti. U každé otázky jsou uvedeny čtyři odpovědi, vždy jen jedna z nich je správná. (Výsledek tohoto kvízu nemá vliv na výši odměny.)
"""

quizInstructions2 = """
Nyní odpovězte na následující otázky týkající se obsahu právě zhlédnutého videa na Chybu Statutu Quo. U každé otázky jsou uvedeny čtyři odpovědi, vždy jen jedna z nich je správná. (Výsledek tohoto kvízu nemá vliv na výši odměny.)
"""

braces = "{}"
quizInstructions3 = f"""
Nyní Vás čeká závěrečný kvíz, který ověří, co jste si z videí zapamatovali.
Za každou správnou odpověď získáte 1 bod. 
U každé otázky je vždy jedna správná odpověď.

Připomínáme, že pokud v závěrečném kvízu obdržíte alespoň {LIMIT} bodů z 25, obdržíte dodatečnou finanční odměnu ve výši {braces} Kč.
"""


class Videos(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.video_path = self.getVideo()

        # Create tkinter canvas for video
        self.canvas = Canvas(self, width=1200, height=674, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.canvas.grid(column = 1, row = 1, sticky=(N, S, E, W))

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 1)

        # Initialize VLC player
        self.instance = vlc.Instance('--vout=direct3d9')
        self.player = self.instance.media_player_new()

        # Set the video output to the tkinter canvas
        self.player.set_hwnd(self.canvas.winfo_id())

        # Load the video file
        media = self.instance.media_new(self.video_path)
        self.player.set_media(media)

        # Bind the VLC event manager to detect when the video ends
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

        # Play the video
        self.player.play()

        ttk.Style().configure("TButton", font="helvetica 15")
        self.next = ttk.Button(self, text="Pokračovat", command=self.stop)
        self.next.grid(row=2, column=1)
        if not TESTING:
            self.next["state"] = "disabled"

    def on_video_end(self, event):
        """Callback for when the video ends."""
        self.next["state"] = "normal"

    def stop(self):
        self.player.stop()
        self.root.status["videoNumber"] += 1
        self.nextFun()

    def getVideo(self):
        trial = self.root.status["videoNumber"]
        return os.path.join(os.getcwd(), "Stuff", "Videos", f"0{trial}.mp4")



class Videos2(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.video_path = self.getVideo()
        self.overlay_enabled = BooleanVar(value=False)
        self.overlay_refresh_job = None
        self.right_overlay_window = None

        # Create video canvas on the left
        self.canvas1 = Canvas(self, width=600, height=337, background="white", highlightbackground="white", highlightcolor="white")
        self.canvas1.grid(column=1, row=1, sticky=(N, S, E, W), padx=5)

        # Create right-side content canvas
        self.canvas2 = Canvas(self, width=600, height=337, background="black", highlightbackground="black", highlightcolor="black")
        self.canvas2.grid(column=2, row=1, sticky=(N, S, E, W), padx=5)
        self.canvas2.bind("<Configure>", self._on_right_canvas_configure)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Initialize VLC player for left video with audio output
        self.instance = vlc.Instance('--aout=waveout', '--vout=direct3d9')
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.canvas1.winfo_id())

        # Load the video file
        media = self.instance.media_new(self.video_path)
        self.player.set_media(media)

        # Track video end
        self.video_ended = False

        # Bind the VLC event manager to detect when video ends
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

        # Play the video
        self.player.play()

        self.content_type = random.choice(["chat", "tiktok", "game"])
        #self.content_type = "chat"  # For testing purposes, you can set this to a specific content type
        content_map = {
            "chat": Chat,
            "tiktok": TikTok,
            "game": Game,
        }
        self.right_content = content_map[self.content_type](self.canvas2, width=400, height=850)
        self.right_content.play()

        ttk.Style().configure("TButton", font="helvetica 15")
        self.next = ttk.Button(self, text="Pokračovat", command=self.stop)
        self.next.grid(row=2, column=1)

        self.overlay_toggle = ttk.Checkbutton(
            self,
            text="Šedý filtr vpravo",
            variable=self.overlay_enabled,
            command=self.toggle_right_overlay
        )
        self.overlay_toggle.grid(row=2, column=2, sticky="e", padx=5)
        if not TESTING:
            self.next["state"] = "disabled"

    def on_video_end(self, event):
        """Callback for when main video ends."""
        self.video_ended = True
        self.next["state"] = "normal"

    def stop(self):
        if self.overlay_refresh_job is not None:
            self.after_cancel(self.overlay_refresh_job)
            self.overlay_refresh_job = None
        self._destroy_right_overlay_window()
        self.player.stop()
        self.right_content.stop()
        self.root.status["videoNumber"] += 1
        self.nextFun()

    def _on_right_canvas_configure(self, event):
        if self.overlay_enabled.get():
            self._position_right_overlay_window()

    def _ensure_right_overlay_window(self):
        if self.right_overlay_window is not None and self.right_overlay_window.winfo_exists():
            return

        self.right_overlay_window = Toplevel(self)
        self.right_overlay_window.overrideredirect(True)
        self.right_overlay_window.configure(background="#808080")
        self.right_overlay_window.attributes("-alpha", 0.45)
        self.right_overlay_window.transient(self.winfo_toplevel())

    def _refresh_right_overlay(self):
        self.overlay_refresh_job = None
        if not self.overlay_enabled.get():
            return

        self._position_right_overlay_window()
        self.overlay_refresh_job = self.after(120, self._refresh_right_overlay)

    def _position_right_overlay_window(self):
        self._ensure_right_overlay_window()
        self.update_idletasks()

        x = self.canvas2.winfo_rootx()
        y = self.canvas2.winfo_rooty()
        width = max(1, self.canvas2.winfo_width())
        height = max(1, self.canvas2.winfo_height())

        self.right_overlay_window.geometry(f"{width}x{height}+{x}+{y}")
        self.right_overlay_window.lift()

    def _destroy_right_overlay_window(self):
        if self.right_overlay_window is not None and self.right_overlay_window.winfo_exists():
            self.right_overlay_window.destroy()
        self.right_overlay_window = None

    def toggle_right_overlay(self):
        if self.overlay_enabled.get():
            self._position_right_overlay_window()
            if self.overlay_refresh_job is None:
                self.overlay_refresh_job = self.after(120, self._refresh_right_overlay)
        else:
            self._destroy_right_overlay_window()
            if self.overlay_refresh_job is not None:
                self.after_cancel(self.overlay_refresh_job)
                self.overlay_refresh_job = None

    def getVideo(self):
        trial = self.root.status["videoNumber"]
        return os.path.join(os.getcwd(), "Stuff", "Videos", f"0{trial}.mp4")


class JOL(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "", proceed = True, savedata = True)

        self.root = root

        q = "Kolik informací z videa si myslíte, že si budete schopni vybavit přibližně za 2-3 minuty?"
        options = ["0 % (nic z toho)", "20 %", "40 %", "60 %", "80 %", "100 % (vše)"]

        self.measure = Measure(self, text = q, values = options, left = "", right = "", questionPosition = "above", filler = 700, function=self.enable)
        self.measure.grid(row = 1, column = 1)

        self.next["state"] = "disabled"

    def enable(self):
        self.next["state"] = "normal"

    def write(self):
        trial = self.root.status["videoNumber"] - 1
        version = self.root.status["versions"][trial - 1]
        self.file.write("JOL\n")
        self.file.write(self.id + "\t" + str(trial) + "\t" + version + "\t" + self.measure.answer.get() + "\n\n")


class Attention(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = attInstructions, proceed = True, savedata = True)

        self.root = root

        self.measure1 = Measure(self, text = attQ1, values = attScale, left = "", right = "", questionPosition = "above", filler = 700, function = self.enable)
        self.measure1.grid(row = 2, column = 1)

        self.measure2 = Measure(self, text = attQ2, values = attScale, left = "", right = "", questionPosition = "above", filler = 700, function = self.enable)
        self.measure2.grid(row = 3, column = 1)

        self.next.grid(row = 4, column = 1)

        self.rowconfigure(0, weight = 3)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 2)
        self.rowconfigure(5, weight = 3)

        self.next["state"] = "disabled"

    def enable(self):
        if self.measure1.answer.get() and self.measure2.answer.get():
            self.next["state"] = "normal"

    def write(self):
        trial = self.root.status["videoNumber"] - 1
        self.file.write("Attention\n")
        self.file.write(self.id + "\t" + str(trial) + "\t" + self.measure1.answer.get() + "\t" + self.measure2.answer.get() + "\n\n")


class Quiz(InstructionsAndUnderstanding):
    def __init__(self, root, name, **kwargs):
        super().__init__(root, width = 80, name = name, randomize = True, showFeedback = False, fillerheight = 300, finalButton = "Pokračovat", **kwargs)

        self.name = name
        self.correct = 0

        self.rowconfigure(0, weight = 5)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1) 
        self.rowconfigure(3, weight = 1)   
        self.rowconfigure(4, weight = 5)

    def nextFun(self):  
        if self.controlQuestion.getAnswer() == self.controlTexts[self.controlNum - 1][1][0]:
            thisCorrect = "1"
            self.correct += 1
        else:
            thisCorrect = "0"
            
        self.file.write(self.id + "\t" + str(self.controlNum) + "\t" + self.controlTexts[self.controlNum - 1][0] + "\t" + self.controlQuestion.getAnswer() + "\t" + thisCorrect + "\t" + str(self.correct) + "\t" + self.root.status["condition"] + "\t" + self.root.status["versions"][int(self.name[-1])-1] + "\n")

        if self.controlNum == len(self.controlTexts):
            self.file.write("\n")
            if self.name == "Quiz3":
                self.root.texts["quizcorrect"] = str(self.correct)
                if self.correct >= LIMIT:
                    self.root.status["quizwin"] = int(self.root.texts["condition"])
                else:
                    self.root.status["quizwin"] = 0
                self.root.texts["quizwin"] = str(self.root.status["quizwin"])
            InstructionsFrame.nextFun(self)   
        else:
            self.createQuestion()     


IMI1 = (Questionnaire,
                {"words": "imi.txt",
                 "question": imiInstructions,
                 "labels": imiScale,
                 "values": 5,
                 "labelwidth": 11,
                 "text": False,
                 "fontsize": 13,
                 "blocksize": 5,
                 "wraplength": 700,
                 "filetext": "IMI1",
                 "fixedlines": 0,
                 "pady": 3})

IMI2 = (Questionnaire,
                {"words": "imi.txt",
                 "question": imiInstructions,
                 "labels": imiScale,
                 "values": 5,
                 "labelwidth": 11,
                 "text": False,
                 "fontsize": 13,
                 "blocksize": 5,
                 "wraplength": 700,
                 "filetext": "IMI2",
                 "fixedlines": 0,
                 "pady": 3})

IMI3 = (Questionnaire,
                {"words": "imi2.txt",
                 "question": imiInstructions2,
                 "labels": imiScale,
                 "values": 5,
                 "labelwidth": 11,
                 "text": False,
                 "fontsize": 13,
                 "blocksize": 5,
                 "wraplength": 700,
                 "filetext": "IMI3",
                 "fixedlines": 0,
                 "pady": 3})


def getQuestions(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), "r", encoding = "utf-8") as f:
        questions = []        
        q = ["", [], ""]
        count = 0
        for line in f:      
            if count == 0:
                q[0] = line.strip().replace("\\n", "\n")
            elif count == 5:                    
                questions.append(q)
                q = ["", [], ""]
                count = -1
            else:
                q[1].append(line.strip())               
            count += 1
    questions.append(q)
    random.shuffle(questions)
    return questions


Quiz1 = (Quiz, {"text": quizInstructions1, "height": 5, "name": "Quiz1", "controlTexts": getQuestions("quiz1.txt")})
Quiz2 = (Quiz, {"text": quizInstructions2, "height": 5, "name": "Quiz2", "controlTexts": getQuestions("quiz2.txt")})
Quiz3 = (Quiz, {"text": quizInstructions3, "height": 8, "name": "Quiz3", "controlTexts": getQuestions("quiz3.txt"), "update": ["condition"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login, Attention, Videos2, Videos])