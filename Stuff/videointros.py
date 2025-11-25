#! python3

from tkinter import *
from tkinter import ttk

import os
import ctypes
import time
import vlc

from common import InstructionsFrame
from gui import GUI
from constants import LIMIT, TESTING
from login import Login


instructions1 = """
Než přistoupíme k hlavní části studie, připravili jsme pro vás krátkou úvodní část, ve které Vás seznámíme s podobou videí, jejich strukturou a způsobem následného vyplňování úkolů.

Nejprve představíme lekci - téma, o kterém všechna videa jsou - tedy jak pořádat pracovní schůzky a porady. Poté uvidíte dvě krátká videa. Každé z nich je zpracováno v odlišném formátu.

Cílem této části je, abyste se seznámili s oběma formáty videí, dali na ně zpětnou vazbu a zároveň si osvojili způsob, jakým probíhá krátký kvíz o obsahu videí. Tato část není nijak peněžně odměněna, slouží k seznámení s průběhem další části studie.
"""

instructions2 = """
Vítejte v lekci zaměřené na porady a pracovní schůzky. Možná se vám při slově „porada“ vybaví spíše frustrace než efektivní komunikace – a účast na školení o poradách může působit ještě o něco absurdněji. Nejste sami.

Podle studií z oblasti organizační psychologie je více než polovina času stráveného na poradách zcela neefektivní. Průměrný zaměstnanec tráví na poradách přibližně 6 hodin týdně, u vedoucích pracovníků to může být až 23 hodin. Schůzky často bývají vnímány jako ztráta času – bez jasného cíle, bez využití schopností účastníků a bez skutečného dopadu na práci.

Všechna videa v této lekci Vám nabídnou konkrétní rady, jak porady vést efektivněji a jak se na nich lépe uplatnit i jako účastník. Doporučení vycházejí z výzkumů v oblasti psychologie a projektového managementu z různých částí světa.

Videa se zaměří na psychologické aspekty – tedy proč porady často nefungují, jaké tendence vedou ke zbytečnému komplikování problémů a proč někdy ztrácíme čas. Videa také nabídnou praktické tipy – nejprve pro organizátory porad, dále pro samotné účastníky a nakonec se zaměří na specifika online meetingů.
"""

instructions3 = """
V následujícím kroku uvidíte první video.

Nyní si nasaďte sluchátka a kliknutím na tlačítko "Test zvuku" ozkoušejte, zda zvuk funguje. Pokud zvuk nefunguje, zkontrolujte prosím nastavení zvuku na Vašich sluchátkách a zkuste to znovu. Pokud problém přetrvává, zavolejte prosím výzkumného asistenta zvednutím ruky.

<b>Poté, co ozkoušíte, že zvuk funguje, klikněte na tlačítko "Pokračovat" a video se spustí automaticky.</b> Po jeho zhlédnutí Vás čeká krátké hodnocení videa a znalostní test.
"""

instructions4 = """
V následujícím kroku uvidíte druhé video ve druhém formátu.

Pokud nemáte nasazená sluchátka, nasaďte si je nyní. Poté klikněte na tlačítko "Pokračovat" a video se spustí automaticky. Po jeho zhlédnutí Vás čeká krátké hodnocení videa a znalostní test.
"""

instructions5 = """
Děkujeme! Právě jste dokončili první část studie.
Zhlédli jste dvě videa ve dvou různých formátech a poskytli nám své hodnocení i odpovědi na kvízové otázky.
"""

instructionsSelection = """Čeká Vás dále série pěti videí, jejich ohodnocení a závěrečný kvíz k této sérii videí, za který již budete odměněni. Otázky opět budou různé náročnosti, od lehkých po zaměřené na detaily výkladu.

Pokud v závěrečném kvízu obdržíte alespoň {} bodů z 25, obdržíte dodatečnou finanční odměnu ve výši {} Kč.

Nyní vás čeká důležité rozhodnutí, tedy, ve kterém formátu videí byste chtěli pokračovat pro sérii pěti videí. 

- <b>Formát na obrázku vlevo</b> je, jak jste viděli, ve formě {}.
- <b>Formát na obrázku vpravo</b> je, jak jste viděli, ve formě {}.

<b>Přestože se videa liší formou, oba formáty obsahují zcela identické informace.</b>

Po zhlédnují všech videí Vás opět čeká jejich hodnocení a finální kvíz z těchto 5 videí. 
Váš výběr formátu vida je důležitý – výše Vaší odměny závisí na úspěšnosti tohoto finálního kvízu.

Formát videa vyberte kliknutím na obrázek."""

Rtext = "statické prezentace s výraznou textovou podporou. V menším okně je osoba, která provádí lekcí"
Stext = "dynamické prezentace hlavních bodů, otázek posluchačům a osoba, která provádí lekcí, je výrazněji přítomna"


instructions6 = """
Děkujeme za Váš výběr.

Nyní přejdeme k sérii pěti videí z lekce zaměřené na porady a pracovní schůzky ve Vámi zvoleném formátu.

Pokud nemáte nasazená sluchátka, nasaďte si je nyní. Poté klikněte na tlačítko "Pokračovat" a první z videí se spustí automaticky.
"""



class Sound(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = instructions3, proceed = True, height = 11, width = 80)    
        self.root = root
        self.sound_file = os.path.join(os.getcwd(), "Stuff", "Videos", "sample.mp3")

        # Initialize VLC player
        self.instance = vlc.Instance()
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
        self.player.play()
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
        




class Selection(InstructionsFrame):
    def __init__(self, root):
        l, r = root.status["versions"]
        t1 = eval(f"{l}text")
        t2 = eval(f"{r}text")
        text = instructionsSelection.format(LIMIT, root.texts["condition"], t1, t2)

        super().__init__(root, text = text, proceed = True, height = 20, width = 90)

        ttk.Style().configure("Padded.TButton", padding = (5,5))        

        self.left = ttk.Button(self, text="", command=lambda: self.response(l))
        self.image_left = PhotoImage(file=os.path.join(os.getcwd(), "Stuff", f"{l}.png"))
        self.left.config(image=self.image_left)
        self.left.image = self.image_left  # Keep a reference to avoid garbage collection
        self.left.grid(row=2, column=1)
        self.left.config(style="Padded.TButton")

        self.right = ttk.Button(self, text="", command=lambda: self.response(r))
        self.image_right = PhotoImage(file=os.path.join(os.getcwd(), "Stuff", f"{r}.png"))
        self.right.config(image=self.image_right)
        self.right.image = self.image_right  # Keep a reference to avoid garbage collection
        self.right.grid(row=2, column=3)
        self.right.config(style="Padded.TButton")

        self.next["state"] = "disabled"
        self.next["text"] = "Vybírám..."
        self.next["width"] = 30

        self.next.grid(row=3, column=1, columnspan=3)
        self.text.grid(row=1, column=1, columnspan=3)

        self.columnconfigure(4, weight = 1)

        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 2)
        self.rowconfigure(3, weight = 1)
        self.rowconfigure(4, weight = 3)


    def response(self, choice):        
        if choice == self.root.status["versions"][0]:
            self.next["text"] = "Potvrzuji výběr formátu VLEVO"
        else:
            self.next["text"] = "Potvrzuji výběr formátu VPRAVO"
        self.next["state"] = "normal"
        self.choice = choice

    def nextFun(self):
        self.root.status["versions"].extend([self.choice for i in range(5)])
        self.file.write("Selection\n" + "\t".join([self.id, self.choice, self.root.status["condition"]]) + "\n\n")
        super().nextFun()






VideoIntro1 = (InstructionsFrame, {"text": instructions1, "proceed": True, "height": 15})
VideoIntro2 = (InstructionsFrame, {"text": instructions2, "proceed": True, "height": 25})
#VideoIntro3 = (InstructionsFrame, {"text": instructions3, "proceed": True, "height": 10})
VideoIntro4 = (InstructionsFrame, {"text": instructions4, "proceed": True, "height": 10})
VideoIntro5 = (InstructionsFrame, {"text": instructions5, "proceed": True, "height": 10})
VideoIntro6 = (InstructionsFrame, {"text": instructions6, "proceed": True, "height": 10})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,  Sound,
    Selection, #
        Sound, VideoIntro1,
        VideoIntro2,
        VideoIntro4,
        Selection])
