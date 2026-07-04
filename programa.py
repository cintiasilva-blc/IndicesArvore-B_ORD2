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

# ============================ CABEÇALHO ==============================

def leCabecalho(arvB) -> int:
    '''Retorna o *rrn* da página raiz (-1 se *arvB* estiver vazia.)'''

    arvB.seek(0, io.SEEK_SET)
    rrn = unpack(FORMATO_CAB, arvB.read(TAM_CAB))[0]
    return rrn

def escreveCabecalho(arvB, rrn: int) -> None:

    arvB.seek(0, io.SEEK_SET)
    cab_bytes = pack(FORMATO_CAB, rrn)
    arvB.write(cab_bytes)

# =========================== LEITURA/ESCRITA DE PÁGINA ===============================
def lePagina(arvB, rrn: int) -> Pagina:
        
    # calcula o byte-offset da página a partir de *rrn*
    offset = rrn * TAM_PAG + TAM_CAB 
    # faz seek no arquivo árvore-B para o byte-offset calculado
    arvB.seek(offset, io.SEEK_SET) 
    # lê do arquivo arvB para pag
    pag_bytes = arvB.read(TAM_PAG)
    elementos_pag = unpack(FORMATO_PAG, pag_bytes)

    # fatia a lista e guarda nos elementos da nova_pag
    nova_pag = Pagina()
    i = 0

    nova_pag.numChaves = elementos_pag[i]
    i +=1

    nova_pag.chaves = []
    for _ in range(ORDEM - 1):
        if elementos_pag[i] == -1:
            nova_pag.chaves.append(None)
        else:
            nova_pag.chaves.append(elementos_pag[i])
        i += 1

    nova_pag.filhos = []
    for _ in range(ORDEM):
        if elementos_pag[i] == -1:
            nova_pag.filhos.append(None)
        else:
            nova_pag.filhos.append(elementos_pag[i])
        i += 1

    nova_pag.offsets = []
    for _ in range(ORDEM - 1):
        if elementos_pag[i] == -1:
            nova_pag.offsets.append(None)
        else:
            nova_pag.offsets.append(elementos_pag[i])
        i += 1
    
    return nova_pag

def escrevePagina(arvB, rrn: int, pag: Pagina) -> None:

    # calcula o byte-offset da página a partir do *rrn*
    offset = rrn * TAM_PAG + TAM_CAB
    # faz seek no arquivo árvore-B para o byte-offset calculado
    arvB.seek(offset, io.SEEK_SET)

    # escreve pag_bytes no arquivo arvB
    valores = []
    valores.append(pag.numChaves)

    for chave in pag.chaves:
        if chave is None:
            valores.append(-1)
        else:
            valores.append(chave)

    for filho in pag.filhos:
        if filho is None:
            valores.append(-1)
        else:
            valores.append(filho)

    for off in pag.offsets:
        if off is None:
            valores.append(-1)
        else:
            valores.append(off)

    pag_bytes = pack(FORMATO_PAG, *valores) # * desempacota a lista como argumentos posicionais
    arvB.write(pag_bytes)

def novoRRN(arvB) -> int:

    arvB.seek(io.SEEK_END)
    offset = arvB.tell()
    return (offset - TAM_CAB) // TAM_PAG

# ================================= BUSCA =================================

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


def buscaNaArvore(arvB, chave: int, rrn):

    if rrn == None:                # CASO BASE, condição de parada da recusão
        return False, None, None
    else:
        pag = lePagina(arvB, rrn)
        achou, pos = buscaNaPagina(chave, pag)
        # pos recebe a posição em que a *chave* ocorre em *pag*
        if achou:
            return True, rrn, pos
        else:
            # busca na pagina filha
            return buscaNaArvore(chave, pag.filhos[pos])
        
# ================== INSERÇÃO, DIVISÃO E PROMOÇÃO =====================

def insereChavePromo(chave: int, offset: int, filhoD: int, pag: Pagina):
    if pag.numChaves == (ORDEM - 1):
        pag.chaves.append(None)
        pag.filhos.append(None)
        pag.offsets.append(None)

    i = pag.numChaves
    while i > 0 and chave < pag.chaves[i-1]:
        pag.chaves[i] = pag.chaves[i-1]
        pag.filhos[i+1] = pag.filhos[i]
        pag.offsets[i] = pag.offsets[i - 1]
        i -= 1
    pag.chaves[i] = chave
    pag.filhos[i+1] = filhoD
    pag.offsets[i] = offset
    pag.numChaves += 1

def divide(chave: int, offset, filhoD: int, pag: Pagina, arvB):

    # insere chave, offset e filhoD em pag
    insereChavePromo(chave, offset, filhoD, pag)
    meio = ORDEM // 2                   # meio recebe ORDEM // 2

    # chavePro recebe pag.chaves[meio]
    chavePro = pag.chaves[meio]         
    offsetPro = pag.offsets[meio]

    filhoDpro = novoRRN(arvB)       # filhoDPro recebe o RRN que pNova terá

    # pAtual recebe o conteúdo de pag até meio
    pAtual = Pagina()
    pAtual.numChaves = meio
    for i in range(meio):
        pAtual.chaves[i] = pag.chaves[i]
        pAtual.offsets[i] = pag.offsets[i]

    for i in range(meio + 1):
        pAtual.filhos[i] = pag.filhos[i]


    # pNova recebe o conteúdo de pag até meio+1
    pNova = Pagina()
    j = 0
    for i in range(meio + 1, pag.numChaves):
        pNova.chaves[j] = pag.chaves[i]
        pNova.offsets[j] = pag.offsets[i]
        j += 1
    j = 0
    for i in range(meio + 1, pag.numChaves + 1):
        pNova.filhos[j] = pag.filhos[i]
        j += 1
    pNova.numChaves = pag.numChaves - meio - 1

    return chavePro, offsetPro, filhoDpro, pAtual, pNova

def insereChave(chave, offset, rrn:int, arvB):
    '''Insere uma chave na árvore B.'''

    # Se a chave for inserida com sucesso, a função retorna Verdadeiro, o RRN da página onde a chave foi inserida, e a posição da chave.
    # Se a chave não for inserida, a função retorna Falso, nulo, e nulo.

def insereChave(arvB, chave: int, offset: int, rrnAtual: int):

    # condição de parada da recursão
    if rrnAtual == -1:
        chavePro = chave
        offsetPro = offset
        filhoDPro = -1
        return chavePro, offsetPro, filhoDPro, True
    else:
        pag = lePagina(arvB, rrnAtual)
        achou, pos = buscaNaPagina(chave, pag)
        if achou:
            print(f'Erro: chave "{chave}" duplicada.')
            return None, None, None, False
        chavePro, offsetPro, filhoDPro, promo = insereChave(arvB,chave,offset,pag.filhos[pos])
        if not promo:
            return None, None, None, False
        else:
            if pag.numChaves < (ORDEM - 1):
                insereChavePromo(chavePro,offsetPro,filhoDPro,pag)
                escrevePagina(arvB, rrnAtual, pag)
                return None, None, None, False
            else:
                chavePro, offsetPro, filhoDPro, pag, novaPag = divide(arvB,chavePro, offsetPro,filhoDPro,pag)
                escrevePagina(arvB, rrnAtual, pag)
                escrevePagina(arvB, filhoDPro, novaPag)
                return chavePro, offsetPro, filhoDPro, True

def insereNaArvore(arvB, chave: int, offset: int, raiz:int):
    '''Insere uma chave na árvore B e atualiza a raiz se necessário.'''

    chavePro, offsetPro, filhoDPro, promo = insereChave(arvB, chave, offset, raiz)
    if promo:
        pNova = Pagina()
        # nova chave da raiz
        pNova.chaves[0] = chavePro
        pNova.offsets[0] = offsetPro
        # filho Esq
        pNova.filhos[0] = raiz
        # filho Dir
        pNova.filhos[1] = filhoDPro
        
        pNova.numChaves = 1
        raiz = novoRRN(arvB)
        escrevePagina(arvB, raiz, pNova)
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
    

    