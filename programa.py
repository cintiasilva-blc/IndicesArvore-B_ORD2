from dataclasses import dataclass
from struct import calcsize, unpack, pack
import io

ORDEM = 5 # Num. máx. de refeências = Num. máx. de descendentes
FORMATO_PAG = f'i{ORDEM-1}i{ORDEM}i{ORDEM-1}i'
TAM_PAG = calcsize(FORMATO_PAG)
FORMATO_CAB = 'i'
TAM_CAB = calcsize(FORMATO_CAB)

class Pagina: 
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)
        self.filhos: list = [None] * ORDEM
        ### espaço para adicionar os byte-offsets dos reg.
        self.offsets: list = [None] * (ORDEM - 1)

# Abre o arquivo para ser utilizado nas funções
arq = open("games.dat", 'rb+')
arvB = open("btree.dat", 'x+')


# =========================== BUSCA ===============================
def lePagina(rrn: int) -> Pagina:
    
    global arvB
    offset = rrn * TAM_PAG + TAM_CAB
    arvB.seek(offset, io.SEEK_SET)
    pag_bytes = arvB.read(TAM_PAG)
    elementos_pag = unpack(FORMATO_PAG, pag_bytes)
    nova_pag = Pagina()
    # fatia a lista e guarda nos elementos da nova_pag
    return nova_pag ]




def escrevePagina(rrn: int, pag: Pagina) -> None:

    offset = rrn 
    arq.seek(offset)
    arq.write()


def buscaNaPagina(chave: int, pag: Pagina) -> tuple[bool, int]:
    '''Busca *chave* em *pag* (busca a chave internamente na pagina)
    Exemplos:
    '''

    # Percorre a pagina até o fim ou até encontrar uma chave <= a chave do parametro
    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos]: 
        pos += 1

    # Se a posição existir na página e a chave dessa posição for igual a do parametro, retorna True e a pos
    # Caso contrário, retorna False e pos
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos                               
    else:
        return False, pos


def buscaNaArvore(chave: int, rrn):
    '''Busca *chave* na Arvore-B
    Exemplos:'''

    if rrn == None:                # CASO BASE, condição de parada da recusão
        return False, None, None
    else:
        pag = lePagina(rrn)
        achou, pos = buscaNaPagina(chave, pag)
        # pos recebe a posição em que a *chave* ocorre em *pag*
        if achou:
            return True, rrn, pos
        else:
            # busca na pagina filha
            return buscaNaArvore(chave, pag.filhos[pos])

   

    