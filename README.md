# Índice com Árvore-B
Este projeto implementa um programa que constrói e mantém um índice estruturado como árvore-B para um arquivo de registros de jogos (games.dat). 
A árvore armazena pares {chave, byte-offset} em um arquivo binário (btree.dat) e nunca é carregada completamente na memória.

# Funcionalidades:
- Criação do índice a partir do arquivo de registros (opção -b)
- Execução de operações de busca e inserção via arquivo (opção -e)
- Impressão do conteúdo da árvore-B (opção -p)

# Como executar:
- Criar índice: python programa.py -b
- Executar operações: python programa.py -e operacoes.txt
- Imprimir árvore: python programa.py -p
