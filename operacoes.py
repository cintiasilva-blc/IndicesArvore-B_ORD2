import programa

def le_registros(nomeArq) -> list[tuple[str, int]]:
    '''Percorre o arquivo inteiro e retorna todos os registros.
    Para cada registro, lê 2 bytes para saber o tamanho e adiciona a string do registro e seu offset na lista de retorno.
    Exemplos:
    >>> registros = le_registros('games.dat')
    >>> registros[0]
    ('484|The Legend of Zelda: Breath of the Wild|2017|Action-Adventure|Nintendo|Nintendo Switch|', 0)
    >>> registros[1]
    ('348|Tetris|1985|Puzzle|Nintendo|Game Boy|', 93)
    '''
    with open(nomeArq, 'rb') as arq: # abre o arquivo 'nomeArq' para leitura  
        registros = []

        off_set = arq.tell() # posição onde o registro começa
        tam_b = arq.read(2) # le dois bytes do arquivo que indicam o tamanho total do registro
        tam = int.from_bytes(tam_b, 'little') # converte o tam_b de byte para inteiro

        while len(tam_b) == 2: 
            reg = arq.read(tam) # lê um registro
            reg_str = reg.decode() # tranforma bytes => string
            registros.append((reg_str, off_set)) # retorna uma lista de tuplas com o offset e o registro
            off_set = arq.tell() # posição onde o registro começa
            tam_b = arq.read(2) # le dois bytes do arquivo, sendo esses o tamanho do registro
            tam = int.from_bytes(tam_b, 'little') # transforma o tam do registro de byte para inteiro        
        return registros

def le_UM_registro(nomeArq, offset: int) -> tuple[str, int]:
    '''Lê um único registro a partir de um byte-offset.
    Retorna a string do registro e o total de bytes ocupados (2 bytes do tamanho + o registro em si).'''
    with open(nomeArq, 'rb') as arq:
        arq.seek(offset)
        tam_b = arq.read(2)
        tam = int.from_bytes(tam_b, 'little')
        reg = arq.read(tam)
        reg_str = reg.decode()
    return reg_str, 2 + tam


def escreverRegistro(nomeArq, campos:list[str]) -> int:
    '''Recebe um arquivo e uma lista de campos do registro, monta a string do registro,
    calcula o tamanho e escreve os 2 bytes de tamanhos seguidos do conteúdo no arquivo. '''
   
    reg = f'{campos[0]}|{campos[1]}|{campos[2]}|{campos[3]}|{campos[4]}|{campos[5]}|' #monta a string do registro

    reg_b = reg.encode() #transforma em bytes
    tam = len(reg_b) # verifica o tamanho do registro
    tam_b = tam.to_bytes(2, 'little')

    nomeArq.write(tam_b) #escreve o tam do registro
    nomeArq.write(reg_b) # escreve o rgeistro

    return 2 + tam # retorna o total de bytes escritos

def inserirRegistro(campos, nomeArq) -> tuple[int, int]:
    ''' Insere um novo registro no final do arquivo games.dat'''

    with open(nomeArq, 'rb+') as arq:
        arq.seek(0, 2) #vai para o final do arq
        offset = arq.tell() # offset do novo registro
        tam_total = escreverRegistro(arq, campos) # escreve o novo registro no final do arq
    return offset, tam_total


def executaOperacoes(nomeArvB:str, nomeArq:str, nomeArqOperacoes:str):
    '''Executa as operações de inserção e busca em uma árvore B a partir de um arquivo de operações.'''
    
    with open(nomeArqOperacoes, 'r') as arq, open(nomeArvB, 'r+b') as arvB:
        raiz = programa.leCabecalho(arvB)
        # encontra o primeiro espaço para separar o identificador do argumento
        for linha in arq:
            i = 0
            tam = len(linha)
    
            while i < tam and linha[i] != ' ':
                i += 1

            op = linha[:i]
            arg = linha[i + 1:]
            
            #remove o \n do final
            if arg != '' and arg[-1] == '\n':
                arg = arg[:-1]
            

            if op == 'b': #busca
                id = int(arg)
                print(f'\nBusca pelo registro de chave "{id}"')
                achou, offset = programa.buscaNaArvore(arvB, id, raiz)
                if achou:
                    reg_str, tam_total = le_UM_registro(nomeArq, offset)
                    print(f'{reg_str} ({tam_total} bytes - offset {offset})')
                else:
                    print(f'Erro: chave "{id}" não encontrada.')
                print()

            elif op == 'i': #inserção
                campos = arg.split('|')
                if campos and campos[-1] == '':
                    campos = campos[:-1]
                id = int(campos[0])
 
                achou, _ = programa.buscaNaArvore(arvB, id, raiz)
                if achou:
                    print(f'Inserção do registro de chave "{id}"')
                    print(f'Erro: chave "{id}" duplicada.')
                else:
                    print(f'Inserção do registro de chave "{id}"')
                    offset,tam_total = inserirRegistro(campos, nomeArq)
                    raiz = programa.insereNaArvore(arvB, id, offset, raiz)
                    programa.escreveCabecalho(arvB, raiz)
                    reg = f'{campos[0]}|{campos[1]}|{campos[2]}|{campos[3]}|{campos[4]}|{campos[5]}|'
                    print(f'{reg} ({tam_total} bytes - offset {offset})')

                print()
        print(f'As operações do arquivo "{nomeArqOperacoes}" foram executadas com sucesso!')

if __name__ == '__main__':
    nomeArvB = 'btree.dat'
    nomeArq = 'games.dat'
    nomeArqOperacoes = 'operacoes.txt'
    executaOperacoes(nomeArvB, nomeArq, nomeArqOperacoes)
