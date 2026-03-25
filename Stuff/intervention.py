from common import InstructionsFrame


nudgeinstructions = """Během sledování videí bude vedlejší panel s rušivými elementy překryt poloprůhledným šedým závojem, který indikuje, že je aktivní "Režim soustředění". Tento režim se automaticky zapne na začátku každého videa. 

Režim soustředění můžete kdykoliv libovolně vypnout nebo zapnout pomocí přepínacího tlačítka na obrazovce."""

boostinstructions = """Shlédněte video níže."""


class Intervention(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = nudgeinstructions, proceed = True, height = "auto", width = 80)