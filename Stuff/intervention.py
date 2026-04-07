#! python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk
import os

from common import ExperimentFrame, InstructionsAndUnderstanding, InstructionsFrame
from gui import GUI
from login import Login
from videos import Videos

############################################################################
# TEXTS intervention

nudgeinstructions = """Během sledování videi bude vedlejší panel překryt poloprůhledným šedým závojem, který indikuje, že je aktivní <b>"Režim soustředění"</b>. Tento režim se automaticky zapne na začátku každého videa. 

Režim soustředění můžete kdykoliv libovolně vypnout nebo zapnout pomocí přepínacího tlačítka na obrazovce."""

boostinstructions = """Nyní se podíváte na krátké video o strategii, kterou můžete použít během následujících videi, aby Vám pomohla lépe se soustředit na učení. Prosíme, poslouchejte pozorně — hned poté budete odpovídat na několik krátkých otázek."""

boostunderstanding = """Nyní zodpovíte několik krátkých otázek k právě zhlédnutému videu. Vyberte vždy jednu správnou odpověď, která nejlépe odpovídá tomu, co bylo ve videu vysvětleno. Po úspěšném zodpovězení otázek budete pokračovat k vytvoření vlastního "když-tak plánu"."""

control_questions = [
    [
        'Co je "když-tak plán"?',
        [
            "Plán, jak zůstat soustředěný po celý experiment bez ohledu na cokoli.",
            "Plán, který propojuje konkrétní signál rozptýlení s konkrétní akcí, kterou provedete.",
            "Připomínka, že rozptýlení škodí učení."
        ],
        ["Ne", "Ano", "Ne"]
    ],
    [
        'Co je část "KDYŽ" v implementačním záměru?',
        [
            "Akce, kterou uděláte, abyste zlepšili svůj výsledek v kvízu.",
            "Konkrétní signál nebo okamžik, který Vám napoví, že Vaše pozornost začíná kolísat.",
            "Shrnutí vzdělávacího videa."
        ],
        ["Ne", "Ano", "Ne"]
    ],
    [
        'Co je část "TAK" v implementačním záměru?',
        [
            'Cíl, například "Chci se více soustředit".',
            "Konkrétní reakce, kterou můžete okamžitě použít k návratu k učení.",
            "Důvod, proč je digitální prostředí rozptylující."
        ],
        ["Ne", "Ano", "Ne"]
    ],
    [
        "Který plán je silnější?",
        [
            "Když se rozptýlím, tak to už znovu neudělám.",
            "Když si všimnu, že jsem rozptýlený/á, znovu se zaměřím a shrnu poslední myšlenku.",
            "Když bude video obtížné, budu se snažit dávat pozor ještě víc než obvykle."
        ],
        ["Ne", "Ano", "Ne"]
    ],
    [
        'Která reakce "TAK" je lepší?',
        [
            "…tak se budu snažit soustředit víc.",
            "…tak si připomenu svůj cíl a znovu si řeknu poslední klíčový bod.",
            "…tak budu doufat, že si zapamatuji, co bylo právě řečeno."
        ],
        ["Ne", "Ano", "Ne"]
    ]
]

when_options = [
    "Když si všimnu, že se dívám, kam bych neměl…",
    "Když si všimnu, že video sleduji jen pasivně…",
    "Když si všimnu, že moje mysl odběhla k něčemu nesouvisejícímu…",
    "Když si uvědomím, že mě rozptýlení pohltilo víc než samotné učení…"
]

then_options = [
    "…tak se jednou krátce nadechnu a vlastními slovy si řeknu poslední klíčovou myšlenku.",
    "…tak si položím otázku 'Jaká byla právě hlavní pointa?' a odpovím si jednou krátkou větou.",
    "…tak pojmenuji poslední pojem, který si z videa pamatuji.",
    "…tak znovu zaměřím oči na to, kam bych měl, tím že si tam posunu kurzor."
]

if_then_plan_instructions = """Nyní si vytvoříte jeden jednoduchý "když-tak plán", který můžete během experimentu použít na podporu svého učení.

Nejprve zvolte jednu část KDYŽ: tedy okamžik, kterého si můžete spolehlivě všimnout, když Vaše pozornost začne odcházet.

Poté zvolte jednu část TAK: tedy krátkou akci, kterou můžete během několika sekund udělat, abyste se vrátil/a k videu a znovu se zasoustředil/a na obsah."""

############################################################################


class Intervention(ExperimentFrame):
    """Intervention class that conditionally shows control, nudge, or boost condition."""
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        
        condition = self.root.status["condition"]
        
        if condition == "control":
            # Immediately proceed to next frame
            self.after(100, self.nextFun)
        elif condition == "nudge":
            # Insert nudge instruction screen as a normal InstructionsFrame step
            self.root.order.insert(self.root.count + 1, NudgeInstructions)
            self.after(100, self.nextFun)
        elif condition == "boost":
            # Insert dedicated boost video step
            self.root.order.insert(self.root.count + 1, BoostVideo)
            self.root.order.insert(self.root.count + 2, BoostUnderstandingCheck)
            self.root.order.insert(self.root.count + 3, IfThenPlanChooser)
            self.after(100, self.nextFun)


class NudgeInstructions(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text=nudgeinstructions, height="auto", font=15)


class IfThenPlanChooser(InstructionsFrame):
    """Frame for choosing if-then plan components."""
    def __init__(self, root):
        super().__init__(root, text=if_then_plan_instructions, height="auto", font=15, proceed=False)
        self.root = root
        self.root.option_add("*TCombobox*Listbox.Font", "helvetica 15")
        
        # Main container
        container = Frame(self, background="white")
        container.grid(row=2, column=1, sticky=(N, S, E, W), padx=20, pady=20)
        
        # KDYŽ section
        when_frame = Frame(container, background="white")
        when_frame.pack(fill=X, pady=10)
        
        ttk.Label(when_frame, text="Zvolte KDYŽ:", background="white",
                 font="helvetica 15").pack(anchor=W, pady=5)
        
        self.when_var = StringVar()
        ttk.Style().configure("Plan.TCombobox", font="helvetica 15")
        self.when_combo = ttk.Combobox(when_frame, textvariable=self.when_var, font = "helvetica 15",
                        values=when_options, state="readonly", width=80,
                        style="Plan.TCombobox")
        self.when_combo.pack(fill=X)
        
        # TAK section
        then_frame = Frame(container, background="white")
        then_frame.pack(fill=X, pady=15)
        
        ttk.Label(then_frame, text="Zvolte TAK:", background="white",
                 font="helvetica 15").pack(anchor=W, pady=5)
        
        self.then_var = StringVar()
        self.then_combo = ttk.Combobox(then_frame, textvariable=self.then_var, font = "helvetica 15",
                                        values=then_options, state="readonly", width=80,
                                        style="Plan.TCombobox")
        self.then_combo.pack(fill=X)
        
        # Buttons
        buttons_frame = Frame(container, background="white")
        buttons_frame.pack(pady=15)
        
        ttk.Style().configure("TButton", font="helvetica 15")
        self.confirm_button = ttk.Button(buttons_frame, text="Potvrdit plán",
                                         command=self.confirm_plan)
        self.confirm_button.pack(padx=5)
        
        # Result (hidden initially)
        self.result_frame = Frame(container, background="white", height=170)
        self.result_frame.pack(fill=X, pady=10)
        self.result_frame.pack_propagate(False)
        self.result_label = ttk.Label(self.result_frame, text="", background="white",
                                      font="helvetica 15", justify=CENTER, wraplength=900)
        self.next = ttk.Button(self.result_frame, text="Pokračovat", command=self.nextFun)
        # Keep top layout stable by reserving this area from the start,
        # but show result controls only after confirmation.
        self.result_placeholder = Frame(self.result_frame, background="white", height=1)
        self.result_placeholder.pack(fill=X, expand=True)
        
        self.file.write("Když-tak plán (výběr)\n")
    
    def confirm_plan(self):
        """Confirm the plan selection."""
        if not self.when_var.get() or not self.then_var.get():
            return
        
        # Disable comboboxes and button
        self.when_combo["state"] = "disabled"
        self.then_combo["state"] = "disabled"
        self.confirm_button["state"] = "disabled"
        
        # Show full plan
        when_part = self.when_var.get().replace("…", "").replace("...", "").strip()
        then_part = self.then_var.get().replace("…", "").replace("...", "").strip()

        if when_part.lower().startswith("když "):
            when_part = when_part[5:].strip()
        if then_part.lower().startswith("tak "):
            then_part = then_part[4:].strip()

        full_plan = f"Když {when_part},\ntak {then_part}"
        self.result_label.config(text=f"Váš plán:\n\n{full_plan}")
        self.result_placeholder.pack_forget()
        self.result_label.pack(pady=15)
        self.next.pack(pady=5)
        
        # Log to file
        self.file.write(self.id + "\t" + full_plan + "\n\n")


class BoostVideo(Videos):
    """Dedicated boost video frame that always plays boost.mp4."""
    def getVideo(self):
        return os.path.join(os.getcwd(), "Stuff", "Videos", "boost.mp4")

    def stop(self):
        self.player.stop()
        self.nextFun()


BoostUnderstandingCheck = (InstructionsAndUnderstanding,
                           {"text": boostunderstanding,
                            "controlTexts": control_questions,
                            "name": "Boost understanding",
                            "showFeedback": True,
                            "randomize": False,
                            "height": "auto",
                            "fillerHeight": 120})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login, Intervention])
