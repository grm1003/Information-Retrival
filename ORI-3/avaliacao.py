import matplotlib.pyplot as plt
import sys

class Avaliacao:
    def __init__(self, arquivo_referencia):
        self.arquivo_referencia = arquivo_referencia
        self.num_consultas, self.resposta_ideal, self.resposta_obtida = self._ler_arquivo_referencia()
        self.precisao_revocacao_por_consulta = self._calcular_precisao_revocacao()
        self.precisao_revocacao_agrupada = self._reagrupar_precisao_por_revocacao()
        self.media_precisao_revocacao = self._calcular_media_precisao_revocacao()

    def _ler_arquivo_referencia(self):
        with open(self.arquivo_referencia, 'r') as arquivo:
            linhas = arquivo.read().split('\n')
            num_consultas = int(linhas[0])  
            if num_consultas < 0:
                print("[ERROR] : O arquivo de referência não contém consultas!\n")
                exit()
            resposta_ideal, resposta_obtida = self._extrair_respostas(linhas, num_consultas)
        return num_consultas, resposta_ideal, resposta_obtida

    def _extrair_respostas(self, linhas, num_consultas):
        resposta_ideal = {i: linhas[i].split(' ') for i in range(1, num_consultas + 1)}
        resposta_obtida = {i - num_consultas: linhas[i].split(' ') for i in range(num_consultas + 1, num_consultas * 2 + 1)}
        return resposta_ideal, resposta_obtida

    def _calcular_precisao_revocacao(self):
        return {consulta: self._calcular_precisao_revocacao_por_consulta(consulta) for consulta in range(1, self.num_consultas + 1)}

    def _calcular_precisao_revocacao_por_consulta(self, consulta):
        docs_relevantes = self.resposta_ideal[consulta]
        docs_recuperados = self.resposta_obtida[consulta]
        qtd_docs_relevantes_observados = 0
        total_docs_observados = 0
        precisao_por_revocacao = {}
        for doc in docs_recuperados:
            total_docs_observados += 1
            if doc in docs_relevantes:
                qtd_docs_relevantes_observados += 1
                revocacao = qtd_docs_relevantes_observados / len(docs_relevantes) * 100
                precisao = qtd_docs_relevantes_observados / total_docs_observados
                precisao_por_revocacao[revocacao] = precisao
        return precisao_por_revocacao

    def _reagrupar_precisao_por_revocacao(self):
        return {consulta: self._agrupar_precisao_por_revocacao(consulta) for consulta in self.precisao_revocacao_por_consulta}

    def _agrupar_precisao_por_revocacao(self, consulta):
        return {i: self._calcular_precisao_agrupada(i, consulta) for i in range(0, 101, 10)}

    def _calcular_precisao_agrupada(self, i, consulta):
        precisoes_validas = [precisao for revocacao, precisao in self.precisao_revocacao_por_consulta[consulta].items() if revocacao >= i]
        return max(precisoes_validas) if precisoes_validas else 0

    def _calcular_media_precisao_revocacao(self):
        return {r: sum(self.precisao_revocacao_agrupada[consulta][r] for consulta in self.precisao_revocacao_agrupada) / self.num_consultas for r in range(0, 101, 10)}

    def escrever_arquivo_media(self):
        with open("media.txt", 'w+') as arquivo:
            arquivo.write(" ".join(map(str, self.media_precisao_revocacao.values())))
            print("O arquivo media.txt foi gerado!\n")

    def plotar_graficos(self):
        revocacoes = list(self.media_precisao_revocacao.keys())
        input("Pressione ENTER para ver os gráficos de precisão por revocação do algoritmo avaliado\n")
        for i in range(1, self.num_consultas + 1):
            self._plotar_grafico_para_consulta(i, revocacoes)
        self._plotar_grafico_media(revocacoes)

    def _plotar_grafico_para_consulta(self, i, revocacoes):
        precisoes = [self.precisao_revocacao_agrupada[i].get(revocacao, 0) * 100 for revocacao in revocacoes]
        plt.title(f"Gráfico de precisão por revocação da consulta {i}")
        plt.ylabel('% Precisão')
        plt.xlabel('% Revocação')
        plt.xticks(range(0, 101, 10))
        plt.plot(revocacoes, precisoes)
        plt.show()

    def _plotar_grafico_media(self, revocacoes):
        precisoes_media = [self.media_precisao_revocacao[revocacao] * 100 for revocacao in revocacoes]
        plt.title('Gráfico da precisão média por revocação do sistema')
        plt.ylabel('% Precisão')
        plt.xlabel('% Revocação')
        plt.xticks(range(0, 101, 10))
        plt.plot(revocacoes, precisoes_media)
        plt.show()

def main():
    if len(sys.argv) != 2:
        print("Uso: python avaliacao.py referencia.txt")
        exit()
    avaliacao = Avaliacao(sys.argv[1])
    avaliacao.escrever_arquivo_media()
    avaliacao.plotar_graficos()

if __name__ == "__main__":
    main()
