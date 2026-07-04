import programa

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

                print()
            print(f'As operações do arquivo "{nomeArqOperacoes}" foram executadas com sucesso!')
 