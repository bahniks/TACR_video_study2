#! python3

from tkinter import *
from tkinter import ttk
from time import sleep

import os
import vlc
import random

from common import ExperimentFrame, Measure, InstructionsFrame, InstructionsAndUnderstanding, TextArea, read_all
from questionnaire import Questionnaire
from gui import GUI
from login import Login
from constants import LIMIT, TESTING
from chat import Chat
from tiktok import TikTok
from game import Game

from constants import QUIZ_BONUS
from questionnaire import MeasureQuestionnaire



############################################################################
# TEXTS videos

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
attQuestions = [attQ1, attQ2]

endQ1 = "Celkově, jak dobře se vám dařilo udržet pozornost na výukových videích?"
endQ2 = "Jak často vaše pozornost odbíhala od výukových videí?"
endQ3 = "Jak často jste se úmyslně snažili vrátit svou pozornost zpět poté, co jste si všimli, že jste nesoustředění?"
endQ4 = "Použili jste nějakou záměrnou strategii, která vám pomohla udržet pozornost?"
endQ5 = "Jak užitečná pro vás tato strategie byla?"
endQ6 = "Stručně ji prosím popište."

endScale1 = ["velmi špatně", "špatně", "středně", "dobře", "velmi dobře"]
endScale2 = ["vůbec", "zřídka", "někdy", "často", "velmi často"]
endScale3 = ["vůbec nebyla užitečná", "spíše nebyla užitečná", "byla do jisté míry užitečná", "spíše byla užitečná", "byla velmi užitečná"]


quizInstructions = f"""U každé otázky je vždy jedna správná odpověď.

Připomínáme, že za každou správnou odpověď obdržíte dodatečnou finanční odměnu ve výši {QUIZ_BONUS} Kč."""


endInstructions = """Výborně, máte za sebou sledování všech výukových videí! 
Než přistoupíme k dotazníkům a závěrečnému kvízu, rádi bychom vás požádali o celkové zhodnocení toho, jak se vám během celého předchozího úkolu dařilo udržet pozornost a zda jste při tom využívali nějaké záměrné strategie.
Odpovídejte prosím co nejupřímněji podle toho, jak jste situaci celkově vnímali."""

############################################################################


_vlc_instance = vlc.Instance('--aout=waveout', '--vout=direct3d9')

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
        self.player = _vlc_instance.media_player_new()

        # Set the video output to the tkinter canvas
        self.player.set_hwnd(self.canvas.winfo_id())

        # Load the video file
        media = _vlc_instance.media_new(self.video_path)
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


class Empty:
    def __init__(self, canvas, width=400, height=850):
        self.canvas = canvas
        self.width = width
        self.height = height

        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.configure(background="white", highlightbackground="white", highlightcolor="white")

    def play(self):
        return

    def stop(self):
        return


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
        self.player = _vlc_instance.media_player_new()
        self.player.set_hwnd(self.canvas1.winfo_id())

        # Load the video file
        media = _vlc_instance.media_new(self.video_path)
        self.player.set_media(media)

        # Track video end
        self.video_ended = False

        # Bind the VLC event manager to detect when video ends
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

        # Play the video
        self.player.play()

        videos2_index = self.root.status.get("videos2_index", 0)
        self.content_type = self.root.status["distractions"][videos2_index]
        self.root.status["videos2_index"] = videos2_index + 1        
        content_map = {
            "chat": Chat,
            "tiktok": TikTok,
            "game": Game,
            "control": Empty
        }
        self.right_content = content_map[self.content_type](self.canvas2, width=400, height=850)
        self.right_content.play()

        ttk.Style().configure("TButton", font="helvetica 15")
        self.next = ttk.Button(self, text="Pokračovat", command=self.stop)
        self.next.grid(row=2, column=1, columnspan=2)

        ttk.Style().configure("Overlay.TCheckbutton", font="helvetica 15", background="white")
        ttk.Style().map("Overlay.TCheckbutton", background=[("active", "white"), ("selected", "white")])
        self.overlay_toggle = ttk.Checkbutton(
            self,
            text="Šedý filtr vpravo",
            variable=self.overlay_enabled,
            command=self.toggle_right_overlay,
            style="Overlay.TCheckbutton",
            takefocus=False,
        )
        self.overlay_toggle.bind("<FocusIn>", lambda event: self.canvas2.focus_set())
        if self.root.status.get("condition") == "nudge":
            self.overlay_toggle.grid(row=2, column=2, padx=5)
            self.overlay_enabled.set(True)
            self.toggle_right_overlay()
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
        self.right_overlay_window.configure(background="#4F4F4F")
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


class Attention(MeasureQuestionnaire):
    def __init__(self, root):
        super().__init__(root, text = attInstructions, questions = attQuestions, options = attScale, questionPosition = "above", filler = 700, labelPosition = "next")

        self.measure1 = self.measures[0]
        self.measure2 = self.measures[1]

    def write(self):
        trial = self.root.status["videoNumber"] - 1
        self.file.write("Attention\n")
        self.file.write(self.id + "\t" + str(trial) + "\t" + self.measure1.answer.get() + "\t" + self.measure2.answer.get() + "\n\n")


class EndQuestionnaire(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = endInstructions, proceed = True, savedata = True)

        self.root = root

        self.measure1 = Measure(self, text = endQ1, values = endScale1, left = "", right = "", questionPosition = "above", filler = 600, function = self.enable, labelPosition = "next")
        self.measure1.grid(row = 2, column = 1)

        self.measure2 = Measure(self, text = endQ2, values = endScale2, left = "", right = "", questionPosition = "above", filler = 600, function = self.enable, labelPosition = "next")
        self.measure2.grid(row = 3, column = 1)

        self.measure3 = Measure(self, text = endQ3, values = endScale2, left = "", right = "", questionPosition = "above", filler = 600, function = self.enable, labelPosition = "next")
        self.measure3.grid(row = 4, column = 1)

        self.strategy_measure = Measure(self, text = endQ4, values = ["Ano", "Ne"], left = "", right = "", questionPosition = "above", filler = 500, function = self.on_strategy_change, labelPosition = "next")
        self.strategy_measure.grid(row = 5, column = 1)

        self.strategy_filler = Canvas(self, background = "white", highlightbackground = "white", highlightcolor = "white", width = 1, height = 200)
        self.strategy_filler.grid(row = 6, column = 2, sticky = "ew", rowspan = 2)

        self.measure5 = Measure(self, text = endQ5, values = endScale3, left = "", right = "", questionPosition = "above", filler = 700, function = self.enable, labelPosition = "next")
        self.measure5.grid(row = 6, column = 1)
        self.measure5.grid_remove()

        self.strategy_text = TextArea(self, endQ6, width = 80, qlines = 1, alines = 3, on_text_change = lambda e: self.enable())
        self.strategy_text.grid(row = 7, column = 1)
        self.strategy_text.grid_remove()

        self.strategy_rating = ""
        self.strategy_text_value = ""

        self.next.grid(row = 8, column = 1)

        self.rowconfigure(0, weight = 2)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 1)
        self.rowconfigure(5, weight = 1)
        self.rowconfigure(6, weight = 1)
        self.rowconfigure(7, weight = 1)
        self.rowconfigure(8, weight = 2)

        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 0)

        self.next["state"] = "disabled"

    def on_strategy_change(self):
        if self.strategy_measure.answer.get() == "Ano":            
            self.measure5.grid()
            self.strategy_text.grid()
            if self.strategy_rating:
                self.measure5.answer.set(self.strategy_rating)
            if self.strategy_text_value:
                self.strategy_text.field.insert("1.0", self.strategy_text_value)
        else:
            self.strategy_rating = self.measure5.answer.get()
            self.strategy_text_value = self.strategy_text.check()
            self.measure5.grid_remove()
            self.strategy_text.grid_remove()                                    
            self.measure5.answer.set("")
            self.strategy_text.field.delete("1.0", "end")            
        self.enable()

    def enable(self):
        base_done = (self.measure1.answer.get() and self.measure2.answer.get() and self.measure3.answer.get() and self.strategy_measure.answer.get())

        if not base_done:
            self.next["state"] = "disabled"
            return

        if self.strategy_measure.answer.get() == "Ano":
            if self.measure5.answer.get() and self.strategy_text.check():
                self.next["state"] = "normal"
            else:
                self.next["state"] = "disabled"
        else:
            self.next["state"] = "normal"

    def write(self):
        strategy_usefulness = self.measure5.answer.get() if self.strategy_measure.answer.get() == "Ano" else ""
        strategy_description = self.strategy_text.check().replace("\n", "  ").replace("\t", " ") if self.strategy_measure.answer.get() == "Ano" else ""

        self.file.write("EndQuestionnaire\n")
        self.file.write("\t".join([self.id, self.measure1.answer.get(), self.measure2.answer.get(), self.measure3.answer.get(), self.strategy_measure.answer.get(), strategy_usefulness, strategy_description]) + "\n\n")

    def gothrough(self):
        random.choice(self.measure1.radios).invoke()
        random.choice(self.measure2.radios).invoke()
        random.choice(self.measure3.radios).invoke()

        if random.choice([True, False]):
            self.strategy_measure.radios[0].invoke()
            self.strategy_text.field.insert("1.0", "Toto je krátké shrnutí strategie pro test.")
            random.choice(self.measure5.radios).invoke()
        else:
            self.strategy_measure.radios[1].invoke()

        self.update()
        sleep(0.5)
        self.next.invoke()


class Quiz(InstructionsAndUnderstanding):
    def __init__(self, root, name, **kwargs):
        super().__init__(root, width = 80, name = name, randomize = True, showFeedback = False, fillerHeight = 300, finalButton = "Pokračovat", **kwargs)

        self.name = name
        self.correct = 0

        self.rowconfigure(0, weight = 5)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1) 
        self.rowconfigure(3, weight = 1)   
        self.rowconfigure(4, weight = 5)

    def nextFun(self):  
        if not "quizwin" in self.root.status:
            self.root.status["quizwin"] = 0

        if self.controlQuestion.getAnswer() == self.controlTexts[self.controlNum - 1][1][0]:
            thisCorrect = "1"
            self.correct += 1
            self.root.status["quizwin"] += QUIZ_BONUS
        else:
            thisCorrect = "0"
            
        self.file.write(self.id + "\t" + str(self.controlNum) + "\t" + self.controlTexts[self.controlNum - 1][0] + "\t" + self.controlQuestion.getAnswer() + "\t" + thisCorrect + "\t" + str(self.correct) + "\n")

        if self.controlNum == len(self.controlTexts):
            self.file.write("\n")
            InstructionsFrame.nextFun(self)   
        else:
            self.createQuestion()     



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


Quiz = (Quiz, {"text": quizInstructions, "height": "auto", "name": "Quiz", "controlTexts": getQuestions("quiz.txt")})



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login, Videos2, EndQuestionnaire, Quiz, Attention, Videos2, Videos])