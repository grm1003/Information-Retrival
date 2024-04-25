#GABRIEL REZENDE MACHADO - 12121BSI217 
import sys
import spacy
import collections
import pathlib


linguagem_processer = spacy.load("pt_core_news_lg")


indice_invertido = {} 

files = {}


def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    # Obtém o caminho do arquivo base da linha de comando
    base = sys.argv[1]

    # Obtém o diretório base onde estão os arquivos 
    base_dir = pathlib.Path(base).parent.resolve()
    
    docs = obter_arquivos_base(base)
   
    gera_indice_invertido(docs, base_dir)
    
    indice_invertido_ordenado = collections.OrderedDict(sorted(indice_invertido.items()))

    # Escreve o índice invertido em um arquivo
    with open("indice.txt", 'w+') as arquivo_indice_invertido:
        for palavra in indice_invertido_ordenado:
            documentos = " ".join(f"{doc},{contagem}" for doc, contagem in indice_invertido[palavra].items())
            arquivo_indice_invertido.write(f"{palavra}: {documentos}\n")

# Função para obter a lista de arquivos na base de documentos
def obter_arquivos_base(base):
    docs = []
    with open(base) as f:
        for line in f:
            docs.append(line.strip())
    return docs


# Função para gerar o índice invertido
def gera_indice_invertido(docs, base_dir):
    cont_arquivo = 0
    for file in docs:
        cont_arquivo += 1
        files[cont_arquivo] = file
        
        caminho_arquivo =  pathlib.Path.joinpath(base_dir, file)
        with open(caminho_arquivo, 'r') as f:
            txt_arquivo = f.read()

            tokens = linguagem_processer(txt_arquivo)

            palavras_lematizadas = []

            for token in tokens:
                if not token.is_stop and not token.is_punct:
                    palavras_lematizadas.append(token.lemma_.lower())
                    

            for palavra in palavras_lematizadas: 
                if palavra.strip(): 
                    if palavra not in indice_invertido.keys():
                        indice_invertido[palavra] = {cont_arquivo: 1}
                    else:
                        if cont_arquivo not in indice_invertido[palavra].keys():
                            indice_invertido[palavra][cont_arquivo] = 1
                        else:
                            indice_invertido[palavra][cont_arquivo] += 1


# Chama a função main() quando  é executado
if __name__ == "__main__":
    main()
