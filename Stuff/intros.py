#! python3

import os
import urllib.request
import urllib.parse

from math import ceil
from time import sleep

from common import InstructionsFrame
from gui import GUI

from constants import PARTICIPATION_FEE, URL, BONUS, QUIZ_BONUS, ATTENTION_BONUS
from login import Login


################################################################################
# TEXTS
intro = """Studie se skládá ze série 8 krátkých výukových videí, která se věnují zvládání stresu, psychologické odolnosti a poskytování zpětné vazby. 

Důležité upozornění k formátu: Během sledování výukového videa (na levé straně obrazovky) se může na pravé straně obrazovky objevit sekundární panel s různým obsahem (např. krátká videa, chat nebo jednoduchá hra). 

Kromě sledování videí budete vyplňovat několik dotazníků. Níže je uveden přehled toho, co Vás čeká:
<b>1) Čtyři videa na téma stresu a psychické odolnosti:</b> po každém videu budete tázáni na vaši pozornost.
<b>2) Čtyři videa na téma efektivní zpětné vazby:</b> po každém videu budete tázáni na vaši pozornost.
<b>3) Dotazníky:</b> budete odpovídat na otázky ohledně Vašich vlastností a postojů.
<b>4) Znalostní kvíz z obsahu výukových videí</b>: absolvujete kvíz, ve kterém můžete získat dodatečnou odměnu.
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



login = """Vítejte na výzkumné studii pořádané Fakultou podnikohospodářskou Vysoké školy ekonomické v Praze! 

Za účast na studii obdržíte {} Kč. Kromě toho můžete vydělat další peníze v průběhu studie na základě vašeho výkonu ve znalostním kvízu ({} Kč za každou správnou odpověď) a za úspěšné zodpovězení otázek kontrolujících pozornost (2x {} Kč)

Studie bude trvat cca 60-90 minut.

Děkujeme, že jste vypnuli své mobilní telefony, a že nebudete s nikým komunikovat v průběhu studie. Pokud s někým budete komunikovat, nebo pokud budete nějakým jiným způsobem narušovat průběh studie, budete požádáni, abyste opustili laboratoř, bez nároku na vyplacení peněz. Používání telefonů či psaní poznámek je během studie zakázáno, pokud budete používat telefon či si budete psát poznámky, budete požádáni, abyste opustili laboratoř bez nároku na vyplacení peněz. Prosíme, dodržujte tato pravidla, aby průběh studie byl pro všechny zúčastněné příjemný.

Pokud jste již tak neučinili, přečtěte si informovaný souhlas a podepište ho.""".format(PARTICIPATION_FEE, QUIZ_BONUS, ATTENTION_BONUS)


################################################################################





class Ending(InstructionsFrame):
    def __init__(self, root):
        root.texts["reward"] = PARTICIPATION_FEE + root.status["bonus"] + root.status["quizwin"]
        root.texts["participation_fee"] = PARTICIPATION_FEE
        root.texts["bonus"] = BONUS
        updates = ["participation_fee", "attention1", "attention2", "bonus", "quizcorrect", "quizwin", "reward"]
        super().__init__(root, text = ending, keys = ["g", "G"], proceed = False, height = "auto", update = updates)
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







Intro = (InstructionsFrame, {"text": intro, "proceed": True, "height": "auto"})
Initial = (InstructionsFrame, {"text": login, "proceed": False, "height": "auto", "keys": ["g", "G"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login,
         Initial, 
         Intro,
         Ending])
