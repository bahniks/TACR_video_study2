#! python3

from tkinter import *
from tkinter import ttk

import os
import ctypes
import time
import vlc

from common import InstructionsFrame
from gui import GUI
from constants import TESTING, QUIZ_BONUS
from login import Login

############################################################################
# TEXTS videointros

soundcheck = """Pro sledování videí je důležité, abyste měli zapnutý zvuk a nasazená sluchátka.

Nyní si nasaďte sluchátka a kliknutím na tlačítko "Test zvuku" ozkoušejte, zda zvuk funguje. Pokud zvuk nefunguje, zkontrolujte prosím nastavení zvuku na Vašich sluchátkách a zkuste to znovu. Pokud problém přetrvává, zavolejte prosím výzkumného asistenta zvednutím ruky.

<b>Poté, co ozkoušíte, že zvuk funguje, klikněte na tlačítko "Pokračovat".</b>"""


videoinstructions = """Celkem budete sledovat osm videí ve dvou modulech. Ke každému videu je navázáno pět otázek v kvízu, který budete vyplňovat před koncem studie, tedy po zhlédnutí videí a vyplnění dotazníků. Celkem tedy bude v kvízu 40 otázek. Kvíz bude obsahovat otázky z každého videa, ale otázky nebudou rozděleny podle videí, takže nebudete vědět, které otázky se vztahují k jakému videu. Za každou správnou odpověď v kvízu získáte 5 Kč. Celkem tedy můžete získat až 200 Kč za správné odpovědi v kvízu.

Videa budou zobrazena na levé straně obrazovky. Během sledování videa se může na pravé straně obrazovky objevit sekundární panel s různým obsahem. <b>Obsahu tohoto panelu se nemusíte všímat a nijak se nevztahuje k obsahu kvízu. Nijak tedy neovlivní Vaši odměnu a nevztahují se k němu žádné další části studie.</b>

Klikněte na tlačítko "Pokračovat"."""


startvideos = """Nyní přejdeme k prvnímu modulu naší studie. Tato část se skládá ze 4 videí, která se zaměřují na téma <b>stresu a psychologické odolnosti</b>.

Po zhlédnutí každého videa Vás požádáme o dvě rychlé odpovědi týkající se Vaší pozornosti.

Pokud nemáte nasazená sluchátka, nasaďte je nyní, abyste mohli sledovat videa se zvukem.

Klikněte na tlačítko "Pokračovat" a video se spustí automaticky."""


secondmoduleintro = """Skvělé, máte za sebou první polovinu videí!

Nyní přejdeme ke druhému modulu, který obsahuje další 4 videa. Tato série se zaměřuje na téma, <b>jak správně poskytovat a přijímat zpětnou vazbu</b>.

Stejně jako v předchozí části Vás po každém videu poprosíme o krátké zhodnocení Vaší pozornosti.

Klikněte na tlačítko "Pokračovat" a video se spustí automaticky."""


quizInstructions = f"""Nyní Vás čeká závěrečný kvíz, který ověří, co jste si z videí zapamatovali.

V kvízu bude celkem 40 otázek, které se budou týkat všech 8 videí, která jste zhlédli. Otázky nebudou rozděleny podle videí, takže nebudete vědět, které otázky se vztahují k jakému videu.

U každé otázky je vždy jedna správná odpověď.

Připomínáme, že <b>za každou správnou odpověď obdržíte dodatečnou finanční odměnu ve výši {QUIZ_BONUS} Kč.</b>"""

############################################################################


class Sound(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = soundcheck, proceed = True, height = 11, width = 80)    
        self.root = root
        self.sound_file = os.path.join(os.path.dirname(__file__), "Videos", "sample.mp3")

        # Initialize VLC player
        self.instance = vlc.Instance('--aout=waveout')
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(self.sound_file)
        self.player.set_media(self.media)
        self.player.audio_set_volume(100)

        # Create buttons
        self.play_button = ttk.Button(self, text="Test zvuku", command=self.play_sound)
        self.play_button.grid(row=2, column=1)        

        if not TESTING:
            self.next["state"] = "disabled"
        self.next.grid(row=2, column=3)

        self.text.grid(row=1, column=0, columnspan=5)

        self.columnconfigure(4, weight = 1)

        self.bind_all("g", self.add_volume_buttons)
        self.bind_all("<Control-Shift-g>", self.forAdjusting)
        self.bind_all("<Control-Shift-G>", self.forAdjusting)
        self.adjusted = False

    def forAdjusting(self, event=None):
        self.root.attributes("-topmost", False)
        self.root.attributes("-fullscreen", False)
        self.root.overrideredirect(False)
        self.adjusted = True

    def add_volume_buttons(self, event=None):
        """Add volume control buttons to the grid."""
        self.decrease_button = ttk.Button(self, text="-", command=self.decrease_volume)
        self.decrease_button.grid(row=3, column=1)

        self.increase_button = ttk.Button(self, text="+", command=self.increase_volume)
        self.increase_button.grid(row=3, column=3)

    def play_sound(self):
        """Play the sound file."""
        self.player.stop()  # Stop any currently playing media
        self.player.set_media(self.instance.media_new(self.sound_file))
        play_result = self.player.play()
        if play_result == -1:
            # Fallback to default audio output if waveout initialization fails.
            self.instance = vlc.Instance()
            self.player = self.instance.media_player_new()
            self.player.set_media(self.instance.media_new(self.sound_file))
            self.player.audio_set_volume(100)
            self.player.play()
        if not TESTING:
            self.root.after(3000, lambda: self.next.config(state="normal"))

    def nextFun(self):
        self.unbind_all("g")
        self.unbind_all("<Control-Shift-g>")
        self.unbind_all("<Control-Shift-G>")
        if self.adjusted and not TESTING:
            self.root.attributes("-topmost", True)
            self.root.attributes("-fullscreen", True)
            self.root.overrideredirect(True)
        self.player.stop()        
        super().nextFun()

    def increase_volume(self):       
        self.press_key(0xAF)

    def decrease_volume(self):              
        self.press_key(0xAE)

    def press_key(self, hexKeyCode):
        ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0x0001, 0)
        time.sleep(0.1)
        ctypes.windll.user32.keybd_event(hexKeyCode, 0, 0x0002, 0)
        


VideoIntro = (InstructionsFrame, {"text": videoinstructions, "proceed": True, "height": "auto"})
StartVideos = (InstructionsFrame, {"text": startvideos, "proceed": True, "height": "auto"})
SecondModuleIntro = (InstructionsFrame, {"text": secondmoduleintro, "proceed": True, "height": "auto"})
QuizIntroduction = (InstructionsFrame, {"text": quizInstructions, "proceed": True, "height": "auto"})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,  Sound])
