#! python3

import os
import urllib.request
import urllib.parse

from math import ceil
from time import sleep

from common import InstructionsFrame
from gui import GUI

from constants import PARTICIPATION_FEE, URL, BONUS
from login import Login


################################################################################
# TEXTS
intro = """
Studie se skládá ze série videí, které se věnují efektivnímu vedení porad. Videa budete hodnotit a po zhlédnutí videí absolvujete znalostní kvíz, ve kterém můžete získat dodatečnou odměnu, která Vám bude vyplacena na konci experimentu. 

Kromě sledování videí budete vyplňovat několik dotazníků. Níže je uveden přehled toho, co Vás čeká:
<b>1) Sedm videí na téma efektivního vedení porad:</b> Vaším úkolem bude videa zhlédnout a následně ohodnotit. Také absolvujete znalostní kvízy. 
<b>2) Odhady vlastního výkonu ve znalostním kvízu</b>
<b>4) Dotazníky:</b> budete odpovídat na otázky ohledně Vašich vlastností a postojů. 
<b>5) Konec studie a platba:</b> poté, co skončíte, půjdete do vedlejší místnosti, kde podepíšete pokladní dokument, na základě kterého obdržíte vydělané peníze v hotovosti. 

V případě, že máte otázky nebo narazíte na technický problém během úkolů, prosíme, zvedněte ruku a tiše vyčkejte příchodu výzkumného asistenta.

Všechny informace, které v průběhu studie uvidíte, jsou pravdivé a nebudete za žádných okolností klamáni či jinak podváděni."""


ending = """Toto je konec experimentu.

Za účast na studii dostáváte {} Kč. 
{} jste správně na kontrolní otázku v dotazníku. {} tedy dodatečných {} Kč. 
V závěrečném kvízu jste dosáhl(a) {} správných odpovědí z 25. Na základě výsledků v závěrečném kvízu získáváte tedy navíc {} Kč.

<b>Vaše odměna za tuto studii je dohromady {} Kč. Napište prosím tuto částku do příjmového dokladu na stole před Vámi.</b> 

Studie založená na datech získaných v tomto experimentu bude volně dostupná na stránkách Centra laboratorního a experimentálního výzkumu FPH VŠE, krátce po vyhodnocení dat a publikaci výsledků. 

Cílem studie bylo zjistit, jaký typ edukačního videa lidé preferují a jak jej hodnotí v různých parametrech oblíbenosti či náročnosti. Studie rovněž nabízela participantům různou velikost odměny - v závislosti do jaké podmínky byli náhodně zařazeni - za správné odpovědi, s cílem ověřit, jak preference participantů ovlivňuje velká či malá odměna.

<b>Žádáme Vás, abyste nesděloval(a) detaily této studie možným účastníkům, aby jejich volby a odpovědi nebyly ovlivněny a znehodnoceny.</b>
  
Můžete si vzít všechny svoje věci a vyplněný příjmový doklad, a aniž byste rušil(a) ostatní účastníky, odeberte se do vedlejší místnosti za výzkumným asistentem, od kterého obdržíte svoji odměnu. 

Toto je konec experimentu. Děkujeme za Vaši účast!
 
Centrum laboratorního a experimentálního výzkumu FPH VŠE""" 



login = """
Vítejte na výzkumné studii pořádané Fakultou podnikohospodářskou Vysoké školy ekonomické v Praze! 

Za účast na studii obdržíte {} Kč. Kromě toho můžete vydělat další peníze v průběhu studie. 

Studie bude trvat cca 50-70 minut.

Děkujeme, že jste vypnuli své mobilní telefony, a že nebudete s nikým komunikovat v průběhu studie. Pokud s někým budete komunikovat, nebo pokud budete nějakým jiným způsobem narušovat průběh studie, budete požádáni, abyste opustili laboratoř, bez nároku na vyplacení peněz. Používání telefonů či psaní poznámek je během studie zakázáno, pokud budete používat telefon či si budete psát poznámky, budete požádáni, abyste opustili laboratoř bez nároku na vyplacení peněz. Prosíme, dodržujte tato pravidla, aby průběh studie byl pro všechny zúčastněné příjemný.

Pokud jste již tak neučinili, přečtěte si informovaný souhlas a podepište ho. 

Klikněte na tlačítko Pokračovat pro přihlášení do studie.
""".format(PARTICIPATION_FEE)


################################################################################





class Ending(InstructionsFrame):
    def __init__(self, root):
        root.texts["reward"] = PARTICIPATION_FEE + root.status["bonus"] + root.status["quizwin"]
        root.texts["participation_fee"] = PARTICIPATION_FEE
        root.texts["bonus"] = BONUS
        updates = ["participation_fee", "attention1", "attention2", "bonus", "quizcorrect", "quizwin", "reward"]
        super().__init__(root, text = ending, keys = ["g", "G"], proceed = False, height = 29, update = updates)
        self.file.write("Ending\n")
        self.file.write(self.id + "\t" + str(root.texts["reward"]) + "\n\n")

    def run(self):
        self.sendInfo()

    def sendInfo(self):
        while True:
            self.update()    
            data = urllib.parse.urlencode({'id': self.root.id, 'round': -99, 'offer': self.root.texts["reward"]})
            data = data.encode('ascii')
            if URL == "TEST":
                response = "ok"
            else:
                try:
                    with urllib.request.urlopen(URL, data = data) as f:
                        response = f.read().decode("utf-8") 
                except Exception:
                    pass
            if "ok" in response:                     
                break              
            sleep(5)







Intro = (InstructionsFrame, {"text": intro, "proceed": True, "height": 20})
Initial = (InstructionsFrame, {"text": login, "proceed": False, "height": 17, "keys": ["g", "G"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,
         Initial, 
         Intro,
         Ending])
