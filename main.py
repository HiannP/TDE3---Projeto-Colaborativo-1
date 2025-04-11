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
import re
from collections import defaultdict
from email.utils import parseaddr

class GrafoEmail:
    def __init__(self):
        self.lista_adj = defaultdict(dict)
        self.grau_entrada = defaultdict(int)
        self.grau_saida = defaultdict(int)
        self.vertices = set()

    def adicionar_email(self, remetente, destinatarios):
        #Adiciona arestas ao grafo e atualiza graus.
        remetente = remetente.lower()
        self.vertices.add(remetente)
        
        for destinatario in destinatarios:
            destinatario = destinatario.lower()
            self.vertices.add(destinatario)
            
            # Atualiza aresta e graus
            if destinatario in self.lista_adj[remetente]:
                self.lista_adj[remetente][destinatario] += 1
            else:
                self.lista_adj[remetente][destinatario] = 1
                self.grau_saida[remetente] += 1
                self.grau_entrada[destinatario] += 1

    # Métodos do Requisito 2
    def get_ordem(self):
        return len(self.vertices)

    def get_tamanho(self):
        return sum(len(vizinhos) for vizinhos in self.lista_adj.values())

    def get_isolados(self):
        return sum(1 for v in self.vertices 
                 if self.grau_saida[v] == 0 and self.grau_entrada[v] == 0)

    def get_20_grau_saida(self):
        return sorted(self.grau_saida.items(), key=lambda x: -x[1])[:20]

    def get_20_grau_entrada(self):
        return sorted(self.grau_entrada.items(), key=lambda x: -x[1])[:20]

    # Utilitários de processamento de email
    @staticmethod
    def extrair_enderecos(cabecalho):
        #Extrai emails de cabeçalhos complexos.#
        if not cabecalho:
            return []
            
        enderecos = []
        partes = cabecalho.split(':', 1)[-1].split(',')
        for parte in partes:
            _, email = parseaddr(parte.strip())
            if email and '@' in email:
                enderecos.append(email.lower())
        return enderecos

    @classmethod
    def processar_arquivo(cls, caminho_arquivo):
        #Processa um único arquivo de email.#
        grafo = cls()
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()

            # Extrai cabeçalhos principais
            from_match = re.search(r'^From:\s*(.*?)$', conteudo, re.M | re.I)
            to_match = re.search(r'^To:\s*(.*?)$', conteudo, re.M | re.I)
            
            remetente = cls.extrair_enderecos(from_match.group(1)) if from_match else []
            destinatarios = cls.extrair_enderecos(to_match.group(1)) if to_match else []

            if remetente and destinatarios:
                grafo.adicionar_email(remetente[0], destinatarios)

            # Processa encaminhamentos
            for enc in re.findall(r'-{5,}.*?Forwarded by.*?-{5,}(.*?)-{5,}', conteudo, re.S):
                from_enc = re.search(r'From:\s*(.*?)$', enc, re.M | re.I)
                to_enc = re.search(r'To:\s*(.*?)$', enc, re.M | re.I)
                
                if from_enc and to_enc:
                    rem_enc = cls.extrair_enderecos(from_enc.group(1))
                    dest_enc = cls.extrair_enderecos(to_enc.group(1))
                    if rem_enc and dest_enc:
                        grafo.adicionar_email(rem_enc[0], dest_enc)

        return grafo

    @classmethod
    def processar_diretorio(cls, diretorio_base):
        """Processa todos os arquivos em um diretório."""
        grafo = cls()
        for root, _, files in os.walk(diretorio_base):
            for file in files:
                caminho = os.path.join(root, file)
                try:
                    grafo_arquivo = cls.processar_arquivo(caminho)
                    # Mescla os grafos
                    for rem, dests in grafo_arquivo.lista_adj.items():
                        grafo.adicionar_email(rem, dests.keys())
                except Exception as e:
                    print(f"Erro ao processar {caminho}: {str(e)}")
        return grafo

    # Métodos auxiliares
    def salvar_lista_adj(self, arquivo_saida):
        with open(arquivo_saida, 'w') as f:
            for rem, dests in self.lista_adj.items():
                arestas = " -> ".join(f"({d}, {p})" for d, p in dests.items())
                f.write(f"{rem}: {arestas}\n")

# Exemplo de uso
if __name__ == "__main__":
    grafo = GrafoEmail.processar_diretorio("Amostra Enron - 2016")
    
    print(f"Vértices: {grafo.get_ordem()}")
    print(f"Arestas: {grafo.get_tamanho()}")
    print(f"Isolados: {grafo.get_isolados()}")
    
    print("\n20 maiores grau de saída:")
    for email, grau in grafo.get_20_grau_saida():
        print(f"{email}: {grau}")
        
    print("\n20 maiores grau de entrada:")
    for email, grau in grafo.get_20_grau_entrada():
        print(f"{email}: {grau}")
    
    grafo.salvar_lista_adj("lista_emails.txt")