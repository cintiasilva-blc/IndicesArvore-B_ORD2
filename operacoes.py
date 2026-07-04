import programa

def escreverRegistro(arq, campos:list[str]) -> int:
    '''Recebe um arquivo e uma lista de campos do registro, monta a string do registro,
    calcula o tamanho e escreve os 2 bytes de tamanhos seguidos do conteúdo no arquivo. '''
   
    reg = f'{campos[0]}|{campos[1]}|{campos[2]}|{campos[3]}|{campos[4]}|{campos[5]}|' #monta a string do registro

    reg_b = reg.encode() #transforma em bytes
    tam = len(reg_b) # verifica o tamanho do registro
    tam_b = tam.to_bytes(2, 'little')

    arq.write(tam_b) #escreve o tam do registro
    arq.write(reg_b) # escreve o rgeistro

    return 2 + tam # retorna o total de bytes escritos

def inserirRegistro(campos, nomeArq):
    ''' Insere um novo registro no final do arquivo games.dat'''
    id = int(campos[0])

    with open(nomeArq, 'rb+') as arq:
        arq.seek(0, 2) #vai para o final do arq
        offset = arq.tell() # offset do novo registro
        escreverRegistro(arq, campos) # escreve o novo registro no final do arq


def executar_operacoes(nomeArquivo:str, nomeArqOperacoes:str):
    '''Executa as operações de inserção e busca em uma árvore B a partir de um arquivo de operações.'''
    with open(nomeArqOperacoes, 'r') as arq:
        # encontra o primeiro espaço para separar o identificador do argumento
        for linha in arq:
            i = 0
            while i < len(linha) and linha[i] == ' ':
                i += 1

            op = linha[:i]
            arg = linha[i + 1:]
            
            #remove o \n do final
            if arg[-1] == '\n':
                arg = arg[:-1]

            if op == 'b': #busca
                id = int(arg)
                print(f'Busca pelo registro de chave "{id}"')
                programa.buscaNaArvore(id, programa.raiz)
                if id == None:
                    print(f'Erro: chave "{id}" não encontrada.')
                print()

            elif op == 'i': #inserção
                campos = arg.split('|')[:-1]
                id = int(campos[0])
                offset = programa.buscaNaArvore(id, programa.raiz)
                if offset != None:
                    print(f'Erro: chave "{id}" duplicada.')
                else:
                    print(f'Inserção do registro de chave "{id}"')
                    programa.raiz = programa.insereNaArvore((id, int(campos[1])), programa.raiz)
                    programa.inserirRegistro(campos, nomeArquivo)

                print()
            print(f'As operações do arquivo "{nomeArqOperacoes}" foram executadas com sucesso!')

if __name__ == '__main__':
    nomeArquivo = 'games.dat'
    nomeArqOperacoes = 'operacoes.txt'
    executar_operacoes(nomeArquivo, nomeArqOperacoes)
 
