from dataclasses import dataclass

ORDEM = 5 # Num. máx. de refeências = Num. máx. de descendentes

class Pagina: 
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM
        ### deve conter um espaço para adicionar os byte-offsets dos reg.




    