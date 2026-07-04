from dataclasses import dataclass
from struct import calcsize, unpack, pack
import io
import sys

ORDEM = 5 # Num. máx. de refeências = Num. máx. de descendentes

FORMATO_PAG = f'i{ORDEM-1}i{ORDEM}i{ORDEM-1}i'
TAM_PAG = calcsize(FORMATO_PAG)
FORMATO_CAB = 'i'
TAM_CAB = calcsize(FORMATO_CAB)

class Pagina: 
    def __init__(self) -> None:
        self.numChaves: int = 0
        self.chaves: list = [None] * (ORDEM - 1)    # NUM. MAXIMO DE CHAVES
        self.filhos: list = [None] * ORDEM          # NUM. MAX DE FILHOS
        # espaço para adicionar os byte-offsets dos reg.
        self.offsets: list = [None] * (ORDEM - 1)   # NUM. MAXIMO DE CHAVES

# Abre o arquivo para ser utilizado nas funções
arq = open("games.dat", 'rb+')
arvB = open("btree.dat", 'wb+')

# =========================== BUSCA ===============================
def lePagina(rrn: int) -> Pagina:
    
    global arvB
    
    # calcula o byte-offset da página a partir de *rrn*
    offset = rrn * TAM_PAG + TAM_CAB 
    # faz seek no arquivo árvore-B para o byte-offset calculado
    arvB.seek(offset, io.SEEK_SET) 
    # lê do arquivo arvB para pag
    pag_bytes = arvB.read(TAM_PAG)
    elementos_pag = unpack(FORMATO_PAG, pag_bytes)
    nova_pag = Pagina()

    # fatia a lista e guarda nos elementos da nova_pag
    nova_pag.numChaves = elementos_pag[0]
    nova_pag.chaves[elementos_pag[1:ORDEM]]
    nova_pag.filhos[elementos_pag[ORDEM:2*ORDEM]]
    nova_pag.offsets[elementos_pag[2*ORDEM:3*ORDEM]]
    
    return nova_pag

def escrevePagina(rrn: int, pag: Pagina) -> None:

    global arvB

    # calcula o byte-offset da página a partir do *rrn*
    offset = rrn * TAM_PAG + TAM_CAB
    # faz seek no arquivo árvore-B para o byte-offset calculado
    arvB.seek(offset, io.SEEK_SET)

    # escreve pag_bytes no arquivo arvB
    valores = ([pag.numChaves] + 
            pag.chaves +
            pag.filhos + 
            pag.offsets)
    
    valores = [-1 if v is None else v for v in valores] # list comprehension que subistiui None por -1, pois pack() só aceita inteiros

    pag_bytes = pack(FORMATO_PAG, *valores) # * desempacota a lista como argumentos posicionais
    arvB.write(pag_bytes)

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
        
# ================== INSERÇÃO, DIVISÃO E PROMOÇÃO =====================
def novoRRN() -> int:
    arvB.seek(io.SEEK_END)
    offset = arvB.tell()
    return (offset - TAM_CAB) // TAM_PAG


def insereChavePromo(chave: int, filhoD: int, pag: Pagina) -> Pagina:
    if pag.numChaves == (ORDEM - 1):
        pag.chaves.append(None)
        pag.filhos.append(None)

    i = pag.numChaves
    while i > 0 and chave < pag.chaves[i-1]:
        pag.chaves[i] = pag.chaves[i-1]
        pag.filhos[i+1] = pag.filhos[i]
        i -= 1
    pag.chaves[i] = chave
    pag.filhos[i+1] = filhoD
    pag.numChaves += 1

def divide(chave: int, filhoD: int, pag: Pagina) -> tuple[int, int, Pagina, Pagina]:
    pNova = insereChavePromo(chave, filhoD, pag)
    meio = ORDEM // 2
    chavePro = pag.chaves[meio]
    filhoDpro = novoRRN()

    # pAtual recebe o conteúdo de pag até meio
    pAtual = Pagina()
    pAtual.numChaves = meio
    pAtual.chaves = pag.chaves[:meio] + [None] * (ORDEM - 1 - meio)
    pAtual.filhos = pag.filhos[:meio + 1] + [None] * (ORDEM - meio - 1)
    pAtual.offsets = pag.offsets[:meio] + [None] * (ORDEM - 1 - meio)

    # pNova recebe o conteúdo de pag até meio+1
    pNova = Pagina()
    pNova.numChaves = ORDEM - meio - 1
    pNova.chaves = pag.chaves[meio + 1:] + [None] * meio
    pNova.filhos = pag.filhos[meio + 1:] + [None] * meio
    pNova.offsets = pag.offsets[meio + 1:] + [None] * meio

    return chavePro, filhoDpro, pAtual, pNova

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
    

    