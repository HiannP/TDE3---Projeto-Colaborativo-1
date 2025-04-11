"""
O objetivo do trabalho consiste em desenvolver um analisador de contatos a partir da base
de dados Enron Email Dataset*. Nesse projeto procura-se explorar uma aplicação prática
da teoria dos grafos que permite extrair informações úteis a partir da rede de contatos
gerada com os e-mails presentes na base de dados.

Requisitos e Funcionalidades:

1) A partir das mensagens de e-mail da base, construa um grafo direcionado
considerando o remetente e o(s) destinatários de cada mensagem. O grafo deve ser
ponderado, considerando a frequência com que um remetente envia uma mensagem
para um destinatário. O grafo também deve ser rotulado, considerando como rótulo
de cada vértice, o endereço de e-mail do usuário. Para demonstrar a criação do
grafo, você deve salvar toda a lista de adjacências em um arquivo texto.

2) Implemente métodos/funções para extrair as seguintes informações gerais
do grafo construído:

    a. O número de vértices do grafo (ordem);

    b. O número de arestas do grafo (tamanho);

    c. O número de vértices isolados;

    d. Os 20 indivíduos que possuem maior grau de saída e os valores correspondentes 
    (de maneira ordenada e decrescente de acordo com o grau);

    e. Os 20 indivíduos que possuem maior grau de entrada e os valores correspondentes 
    (de maneira ordenada e decrescente de acordo com o grau).

3) Implemente uma função que verifica se o grafo é Euleriano (ou seja, que
possui um ciclo Euleriano), retornando true ou false. Caso a resposta seja false, a
sua função deve informar ao usuário todas as condições que não foram satisfeitas.

4) Implemente um método que retorne uma lista com todos os vértices que
estão localizados até uma distância D de um vértice N, em que D é a soma dos
pesos ao longo do caminho mais curto entre dois vértices. A implementação deve
ser eficiente o suficiente para lidar com grafos com milhares de vértices e arestas
sem exceder limites razoáveis de tempo e memória.

5) Implemente um método que calcule o diâmetro de um grafo, ou seja, o
maior caminho mínimo entre qualquer par de vértices. O algoritmo deve retornar o
valor desse maior caminho mínimo (diâmetro) e o caminho correspondente
encontrado. Por simplicidade, desconsidere que o caminho mínimo entre dois
vértices de componentes diferentes é infinito.

Não serão considerados o uso de bibliotecas para grafos que já implementam as
estruturas de dados ou funções solicitadas
"""

import os
from collections import defaultdict

class GrafoEmail:
    def __init__(self):
        self.lista_adj = defaultdict(dict)
        self.ordem = 0
        self.tamanho = 0

    # Adiciona um e-mail ao grafo, atualizando a lista de adjacências e incrementando a ordem e o tamanho do grafo
    def adicionar_email(self, remetente, destinatarios):
        """
        Adiciona um e-mail ao grafo, atualizando a lista de adjacências.
        :param remetente: Endereço de e-mail do remetente.
        :param destinatarios: Lista de endereços de e-mail dos destinatários.
        """
        # Adiciona o remetente como vértice, mesmo que ele não tenha destinatários
        if remetente not in self.lista_adj:
            self.lista_adj[remetente] = {}
            self.ordem += 1

        # Adiciona os destinatários como vértices, mesmo que eles não tenham arestas de saída
        for destinatario in destinatarios:
            if destinatario not in self.lista_adj:
                self.lista_adj[destinatario] = {}
                self.ordem += 1

            # Incrementa o peso da aresta ou cria uma nova
            if destinatario in self.lista_adj[remetente]:
                self.lista_adj[remetente][destinatario] += 1
            else:
                self.lista_adj[remetente][destinatario] = 1
                self.tamanho += 1
    
    # Função para salvar a lista de adjacências em um arquivo texto
    def salvar_lista_adjacencias(self, arquivo_saida):
        """
        Salva a lista de adjacências em um arquivo texto no formato especificado.
        :param arquivo_saida: Caminho do arquivo de saída.
        """
        with open(arquivo_saida, 'w') as f:
            for remetente, destinatarios in self.lista_adj.items():
                # Formatar as arestas e pesos no formato solicitado
                arestas_formatadas = " -> ".join([f"('{destinatario}', {peso})" for destinatario, peso in destinatarios.items()])
                f.write(f"{remetente}: {arestas_formatadas}\n")

    # Função para obter o número de vértices (ordem do grafo)
    def get_ordem(self):
        """
        Retorna o número de vértices do grafo.
        :return: Número de vértices (ordem do grafo).
        """
        return self.ordem

    # Função para obter o número de arestas (tamanho do grafo)
    def get_tamanho(self):
        """
        Retorna o número de arestas do grafo.
        :return: Número de arestas (tamanho do grafo).
        """
        return self.tamanho

    # Função para obter o número de vértices isolados
    def get_isolados(self):
        """
        Retorna o número de vértices isolados no grafo.
        Um vértice é isolado se não possui arestas de entrada nem de saída.
        :return: Número de vértices isolados.
        """
        isolados = 0
        for vertice, adjacentes in self.lista_adj.items():
            # Verifica se o vértice não possui arestas de saída
            if not adjacentes:
                # Verifica se o vértice não possui arestas de entrada
                possui_entrada = any(vertice in self.lista_adj[remetente] for remetente in self.lista_adj)
                if not possui_entrada:
                    isolados += 1
        return isolados


# Função para processar os e-mails no diretório base e construir o grafo
def processar_emails(diretorio_base, grafo):
    """
    Processa os arquivos de e-mail no diretório base e atualiza o grafo.
    :param diretorio_base: Caminho para o diretório base contendo os e-mails.
    :param grafo: Instância de GrafoEmail.
    """
    for root, _, files in os.walk(diretorio_base):
        for file in files:
            caminho_arquivo = os.path.join(root, file)
            with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                linhas = f.readlines()
                remetente = None
                destinatarios = []
                for linha in linhas:
                    if linha.lower().startswith("from:"):
                        remetente = linha.split(":")[1].strip()
                        # Adiciona o remetente ao grafo, mesmo que ele não tenha destinatários
                        if remetente:
                            grafo.adicionar_email(remetente, [])
                    elif linha.lower().startswith("to:"):
                        destinatarios = [email.strip() for email in linha.split(":")[1].split(",")]
                        # Adiciona os destinatários ao grafo, mesmo que não tenham arestas de saída
                        for destinatario in destinatarios:
                            grafo.adicionar_email(destinatario, [])
                # Adiciona a conexão entre remetente e destinatários, se existirem
                if remetente and destinatarios:
                    grafo.adicionar_email(remetente, destinatarios)

# Exemplo de uso
grafo = GrafoEmail()

# Diretório base contendo os e-mails
diretorio_base = r"c:\Users\padil\OneDrive\Documentos\TDE3 - Projeto Colaborativo 1\Amostra Enron - 2016"

# Processar os e-mails e construir o grafo
processar_emails(diretorio_base, grafo)

# Salvar a lista de adjacências em um arquivo
grafo.salvar_lista_adjacencias("lista_adjacencias.txt")

# Obter informações gerais do grafo
print("Número de vértices (ordem):", grafo.get_ordem())
print("Número de arestas (tamanho):", grafo.get_tamanho())
print("Número de vértices isolados:", grafo.get_isolados())