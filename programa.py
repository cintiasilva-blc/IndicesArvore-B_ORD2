import sys
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

arq = open("games.dat", 'rb+')

# =========================== BUSCA ===============================
def lePagina(rrn: int) -> Pagina:
    
    global arvB
    offset = rrn * TAM_PAG + TAM_CAB
    arvB.seek(offset, io.SEEK_SET)
    pag_bytes = arvB.read(TAM_PAG)
    elementos_pag = unpack(FORMATO_PAG, pag_bytes)
    nova_pag = Pagina()
    # fatia a lista e guarda nos elementos da nova_pag
    return nova_pag 



def escrevePagina(rrn: int, pag: Pagina) -> None:

    byteOffset = rrn * TAM_PAG + TAM_CAB
    arq.seek(byteOffset, io.SEEK_SET)
    pag_bytes = arvB.write(pack(FORMATO_PAG, pag.numChaves, pag.chaves, pag.filhos, pag.offsets))



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

    if rrn == None:              
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

def divide(chave: tuple[int,int], filhoD: tuple[int,int], pag: Pagina):
    '''Divide uma página da árvore B e retorna a chave promovida, o RRN do filho direito promovido, a página dividida, e a nova página.'''

    insereChavePromo(chave, filhoD, pag)
    meio = pag.numChaves // 2
    chavePro = pag.chaves[meio]
    filhoDPro = novoRRN()
    pAtual = pag.chaves[:meio]
    pNova = pag.chaves[meio+1:]
    return chavePro, filhoDPro, pAtual, pNova

def novoRRN():
    '''Gera um novo RRN que a pNova terá no arquico arvore-b.'''
    arvB.seek(0, 2)
    offset = arvB.tell()
    FMT_PAG = f'{ORDEM - 1}i{ORDEM - 1}i{ORDEM}i'
    TAM_PAG = Pagina.calcsize(FMT_PAG)
    FMT_CAB = 'i'
    TAM_CAB = Pagina.calcsize(FMT_CAB)
    return (offset - TAM_CAB) // TAM_PAG

    
def buscaNaPagina(chave:int, pag:Pagina):
    '''Busca uma chave em uma página da árvore B e retorna Verdadeiro e a posição da chave se encontrada, ou Falso e pos contrário.'''

    pos = 0
    while pos < pag.numChaves and chave > pag.chaves[pos]:
        pos += 1
    if pos < pag.numChaves and chave == pag.chaves[pos]:
        return True, pos
    else:
        return False, pos
    
def insereChave(chave:tuple[int,int], rrn:int):
    '''Insere uma chave na árvore B.'''

    # Se a chave for inserida com sucesso, a função retorna Verdadeiro, o RRN da página onde a chave foi inserida, e a posição da chave.
    # Se a chave não for inserida, a função retorna Falso, nulo, e nulo.

    if rrn == None:
        chavePro = chave
        filhoDpro = None
        return chavePro, filhoDpro, True
    else:
        pag = lePagina(rrn)
        achou, pos = buscaNaPagina(chave, pag)
    if achou:
        print("Erro! Chave duplicada.")
    chavePro, filhoDpro, promo = insereChave(chave, pag.filhos[pos])
    if not promo:
        return None, None, False
    else:
        if pag.numChaves < ORDEM - 1:
            pag = insereChave(chavePro,filhoDPro)
            escrevePagina(pag, rrn)
            return None, None, False
        else:
            chavePro, filhoDPro, pag, novaPag = divide(chavePro, filhoDpro, pag)
            rrn = escrevePagina(pag, rrn)
            filhoDPro = escrevePagina(novaPag, novoRRN())
            return chavePro, filhoDPro, True
            

def insereChavePromo(chave:tuple[int,int], filhoDPro:tuple[int,int], pag:Pagina):
    '''Insere uma chave promovida em uma página da árvore B.'''
    if pag.numChaves < ORDEM - 1:
        i = pag.numChaves
        while i > 0 and chave < pag.chaves[i-1]:
            pag.chaves[i] = pag.chaves[i-1]
            pag.filhos[i+1] = pag.filhos[i]
            i -= 1
        pag.chaves[i] = chave
        pag.filhos[i+1] = filhoDPro
        pag.numChaves += 1

def insereNaArvore(chave:tuple[int,int], raiz:tuple[int,int]):
    '''Insere uma chave na árvore B e atualiza a raiz se necessário.'''

    chavePro, filhoDPro, promo = insereChave(chave, raiz)
    if promo:
        pNova = Pagina()
        pNova.chaves[0] = chavePro
        pNova.filhos[0] = raiz
        pNova.filhos[1] = filhoDPro
        pNova.numChaves += 1
        arvB.write(pNova)
        raiz = novoRRN()
    return raiz

def main()-> None:
    '''Função responsável por abrir ou criar o arquivo da arvoreB e chamar a inserção.'''
    # Abre o arquivo para ser utilizado nas funções
    if len(sys.argv) < 2:
        print('Uso: python programa.py -b | -e arquivoOperacoes | -c')
        return
    
    flag = sys.argv[1]
    



if __name__ == "__main__":
    main()
    

    