#GABRIEL REZENDE MACHADO - 12121BSI217 
import collections
import sys
import spacy
import pathlib
import math
import os

linguagem_processer = spacy.load("pt_core_news_lg")

indice_invertido = {} 

def obter_arquivos_base(base):
    if '\\' in base: 
        base_dir = base.split('\\')[0]   
    else:
        base_dir = os.getcwd()
    base = os.path.join(os.getcwd(), base)
    docs = []
    with open(base) as f:
        for line in f:
            docs.append(line.rstrip("\n"))
        f.close()

    return docs, base_dir

def gera_indice_invertido(docs, base_dir):
    cont_arquivo = 0
    global indice_invertido
    for file in docs:
        cont_arquivo += 1
        caminho_arquivo = pathlib.Path(base_dir, file)
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

def responder_consulta(consulta, documentos, matriz_tf_idf):
    query_dict = process_query(consulta)
    documentos_relevantes = []
    def somatoria_quadrado_pesos_arquivo(pesos):
        return sum(peso ** 2 for peso in pesos.values())
    query_norm = math.sqrt(somatoria_quadrado_pesos_arquivo(query_dict))
    for i, doc in enumerate(documentos):
        peso = matriz_tf_idf[i]
        if any(termo in peso for termo in query_dict.keys()):
            dot_product = sum(query_dict.get(termo, 0) * peso.get(termo, 0) for termo in set(query_dict).union(peso))
            doc_norm = math.sqrt(somatoria_quadrado_pesos_arquivo(peso))
            if query_norm != 0 and doc_norm != 0:
                similaridade = dot_product / (query_norm * doc_norm)
                if similaridade > 0:
                    documentos_relevantes.append((similaridade, doc))
    documentos_relevantes.sort(reverse=True)
    return documentos_relevantes

def calcular_tf_idf(docs, indice_invertido, base_dir):
    tf_idf_matrix = []
    cont_arquivo = 0  
    for file in docs:
        cont_arquivo += 1
        caminho_arquivo = pathlib.Path(base_dir, file)
        with open(caminho_arquivo, 'r') as f:
            txt_arquivo = f.read()

            tokens = linguagem_processer(txt_arquivo)

            term_frequency = {}

            for token in tokens:
                if not token.is_stop and not token.is_punct:
                    lemma = token.lemma_.lower()
                    if lemma in term_frequency:
                        term_frequency[lemma] += 1
                    else:
                        term_frequency[lemma] = 1

        tf_idf_doc = {}
        for term, frequency in term_frequency.items():
            if frequency > 0 and term in indice_invertido:
                tf_idf_doc[term] = (1 + math.log10(frequency)) * math.log10(len(docs) / len(indice_invertido[term]))


        tf_idf_matrix.append(tf_idf_doc)

    return tf_idf_matrix


def process_query(query):
    terms = query.split('&')
    query_dict = {}
    for term in terms:
        term = term.strip().lower()
        if term:
            if term not in query_dict:
                query_dict[term] = 1
            else:
                query_dict[term] += 1
    return query_dict

def main():
    # Obtém o caminho do arquivo base da linha de comando
    base = sys.argv[1]
    # Obtém o caminho do arquivo da consulta a ser feita 
    consulta = sys.argv[2]

    # Obtém o diretório base onde estão os arquivos 
    base_consulta = pathlib.Path(consulta).parent.resolve()
    
    docs = []
    docs, base_dir = obter_arquivos_base(base)
    
    with open(base_consulta / consulta, 'r') as f:
        query = f.read().strip()
   
    gera_indice_invertido(docs, base_dir)
    tf_idf_matrix = calcular_tf_idf(docs, indice_invertido, base_dir)
    relevant_docs = responder_consulta(query, docs, tf_idf_matrix)
    
   
    with open("indice.txt", 'w+') as arquivo_indice_invertido:
        indice_invertido_ordenado = collections.OrderedDict(sorted(indice_invertido.items()))
        for palavra in indice_invertido_ordenado:
            documentos = " ".join(f"{doc},{contagem}" for doc, contagem in indice_invertido[palavra].items())
            arquivo_indice_invertido.write(f"{palavra}: {documentos}\n")

    with open("pesos.txt", 'w+') as arquivo_pesos:
        for i, doc in enumerate(docs):
            print(tf_idf_matrix[i].items()) 
            arquivo_pesos.write(f'{doc}: {" ".join(f"{term},{weight}" for term, weight in tf_idf_matrix[i].items() if weight > 0)}\n')

    with open("resposta.txt", 'w+') as arquivo_resposta:
        arquivo_resposta.write(f'{len(relevant_docs)}\n')
        for similarity, doc in relevant_docs:
            arquivo_resposta.write(f'{doc} {similarity}\n')

if __name__ == "__main__":
    main()


