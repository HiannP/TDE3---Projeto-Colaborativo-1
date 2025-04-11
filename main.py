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

import os  # Apenas para ler arquivos do sistema operacional
import re  # Para processar texto
import heapq  # Biblioteca padrão do Python para filas de prioridade
from collections import defaultdict  # Para dicionários com valores padrão
from email.utils import parseaddr # Para extrair endereços de email

class GrafoEmail:
    def __init__(self):
        self.lista_adj = defaultdict(dict)
        self.grau_entrada = defaultdict(int)
        self.grau_saida = defaultdict(int)
        self.vertices = set()  # Todos os emails únicos (remetentes e destinatários)
        self.ordem = 0
        self.tamanho = 0

    def adicionar_email(self, remetente, todos_destinatarios):
        # Adiciona arestas do remetente para todos os destinatários (To, Cc, Bcc)
        if not remetente or not todos_destinatarios:
            return

        # Normaliza remetente e verifica se é novo
        remetente = self._normalizar_email(remetente)
        if remetente not in self.vertices:
            self.vertices.add(remetente)
            self.ordem += 1

        # Adiciona arestas para cada destinatário
        for destinatario in todos_destinatarios:
            destinatario = self._normalizar_email(destinatario)
            if not destinatario or destinatario == remetente:
                continue  # Ignora autoenvios

            # Adiciona destinatário como vértice se for novo
            if destinatario not in self.vertices:
                self.vertices.add(destinatario)
                self.ordem += 1

            # Atualiza aresta e graus
            if destinatario not in self.lista_adj[remetente]:
                self.lista_adj[remetente][destinatario] = 1
                self.tamanho += 1
            else:
                self.lista_adj[remetente][destinatario] += 1

            self.grau_saida[remetente] += 1
            self.grau_entrada[destinatario] += 1

    def _normalizar_email(self, email):
        # Extrai apenas o endereço de email, removendo nomes e espaços.
        if not email:
            return None
        _, email = parseaddr(email.strip())
        return email.lower() if email and '@' in email else None

    # Métodos otimizados
    def get_ordem(self):
        return self.ordem

    def get_tamanho(self):
        return self.tamanho

    def get_isolados(self):
        return sum(1 for v in self.vertices 
                 if self.grau_entrada[v] == 0 and self.grau_saida[v] == 0)

    def get_20_grau_saida(self):
        return sorted(self.grau_saida.items(), key=lambda x: -x[1])[:20]

    def get_20_grau_entrada(self):
        return sorted(self.grau_entrada.items(), key=lambda x: -x[1])[:20]

    def is_euleriano(self):
        """
        Verifica se o grafo direcionado possui um ciclo Euleriano.
        Retorna (True, []) se for Euleriano, 
        ou (False, [condições_falhas]) caso contrário.
        """
        falhas = []
        
        # Verificação 1: Grafo não vazio
        if self.tamanho == 0:
            falhas.append("O grafo não possui arestas")
            return (False, falhas)
        
        # Verificação 2: Graus de entrada e saída iguais para todos os vértices
        graus_iguais = all(self.grau_entrada[v] == self.grau_saida[v] for v in self.vertices)
        if not graus_iguais:
            falhas.append("Nem todos os vértices têm grau de entrada igual ao grau de saída")
        
        # Verificação 3: Fortemente conexo (para vértices com grau > 0)
        vertices_ativos = {v for v in self.vertices if self.grau_entrada[v] > 0 or self.grau_saida[v] > 0}
        if not self._is_fortemente_conexo(vertices_ativos):
            falhas.append("O grafo não é fortemente conexo")
        
        return (True, []) if not falhas else (False, falhas)

    def _is_fortemente_conexo(self, vertices):
        # Verifica se o grafo é fortemente conexo usando DFS
        if not vertices:
            return False
        
        inicio = next(iter(vertices))
        
        # DFS no grafo original
        visitados = set()
        self._dfs(inicio, visitados)
        if visitados != vertices:
            return False
        
        # DFS no grafo transposto
        visitados_transposto = set()
        self._dfs_transposto(inicio, visitados_transposto)
        return visitados_transposto == vertices

    def _dfs(self, vertice, visitados):
        # Busca em profundidade padrão
        visitados.add(vertice)
        for vizinho in self.lista_adj.get(vertice, {}):
            if vizinho not in visitados:
                self._dfs(vizinho, visitados)

    def _dfs_transposto(self, vertice, visitados):
        # Busca em profundidade no grafo transposto
        visitados.add(vertice)
        for v in self.lista_adj:
            if vertice in self.lista_adj[v] and v not in visitados:
                self._dfs_transposto(v, visitados)

    def vertices_ate_distancia(self, vertice, D):
        """
        Retorna todos os vértices até distância D do vértice dado, onde a distância
        é a soma dos pesos ao longo do caminho mais curto.
        """
        if vertice not in self.vertices:
            return []

        # Inicializa estruturas de dados
        distancias = {v: float('inf') for v in self.vertices}
        distancias[vertice] = 0
        fila_prioridade = [(0, vertice)]
        visitados = set()
        vertices_no_alcance = []

        while fila_prioridade:
            dist_atual, v_atual = heapq.heappop(fila_prioridade)
            
            # Se já visitamos este vértice com distância menor, pulamos
            if v_atual in visitados:
                continue
                
            visitados.add(v_atual)
            
            # Se está dentro do alcance, adiciona à lista de resultados
            if dist_atual <= D:
                vertices_no_alcance.append(v_atual)
            else:
                # Como estamos usando uma fila de prioridade, podemos parar aqui
                # pois todas as distâncias restantes serão maiores
                continue
                
            # Explora vizinhos
            for vizinho, peso in self.lista_adj.get(v_atual, {}).items():
                nova_distancia = dist_atual + peso
                
                # Se encontramos um caminho mais curto para o vizinho
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    heapq.heappush(fila_prioridade, (nova_distancia, vizinho))
        
        return vertices_no_alcance

    def calcular_diametro(self):
        # Calcula o diâmetro do grafo (maior caminho mais curto)
        diametro = 0
        caminho_diametro = []
        vertices_ativos = [v for v in self.vertices if self.grau_entrada[v] > 0 or self.grau_saida[v] > 0]
        
        for v in vertices_ativos:
            distancias, predecessores = self._dijkstra(v)
            for u, dist in distancias.items():
                if dist != float('inf') and dist > diametro:
                    diametro = dist
                    caminho_diametro = self._reconstruir_caminho(predecessores, v, u)
        
        return diametro, caminho_diametro

    def _dijkstra(self, origem):
        # Implementação do algoritmo de Dijkstra para caminhos mais curtos
        distancias = {v: float('inf') for v in self.vertices}
        predecessores = {v: None for v in self.vertices}
        distancias[origem] = 0
        fila = [(0, origem)]
        
        while fila:
            dist_atual, v_atual = heapq.heappop(fila)
            if dist_atual > distancias[v_atual]:
                continue
                
            for vizinho, peso in self.lista_adj.get(v_atual, {}).items():
                nova_dist = dist_atual + peso
                if nova_dist < distancias[vizinho]:
                    distancias[vizinho] = nova_dist
                    predecessores[vizinho] = v_atual
                    heapq.heappush(fila, (nova_dist, vizinho))
        
        return distancias, predecessores

    def _reconstruir_caminho(self, predecessores, origem, destino):
        # Reconstroi o caminho a partir dos predecessores
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = predecessores[atual]
        caminho.reverse()
        return caminho if caminho[0] == origem else []

    # Utilitários de processamento de email
    @staticmethod
    def extrair_enderecos(cabecalho):
        # Extrai emails de cabeçalhos complexos
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
        # Extrai remetente (From) e todos os destinatários (To, Cc, Bcc)
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read()

            # Extrai remetente (From)
            remetente = None
            from_match = re.search(r'^From:\s*(.*?)$', conteudo, re.M | re.I)
            if from_match:
                remetente = parseaddr(from_match.group(1))[1]

            # Extrai todos os destinatários (To, Cc, Bcc)
            todos_destinatarios = []
            for campo in ['To', 'Cc', 'Bcc']:
                match = re.search(rf'^{campo}:\s*(.*?)$', conteudo, re.M | re.I)
                if match:
                    destinatarios = [parseaddr(addr)[1] for addr in match.group(1).split(',') if parseaddr(addr)[1]]
                    todos_destinatarios.extend(destinatarios)

            return remetente, todos_destinatarios

    @classmethod
    def processar_diretorio(cls, diretorio_base):
        # Processa todos os arquivos no diretório e subdiretórios
        grafo = cls()
        for root, _, files in os.walk(diretorio_base):
            for file in files:
                caminho = os.path.join(root, file)
                try:
                    remetente, todos_destinatarios = cls.processar_arquivo(caminho)
                    if remetente and todos_destinatarios:
                        grafo.adicionar_email(remetente, todos_destinatarios)
                except Exception as e:
                    print(f"Erro no arquivo {file}: {str(e)}")
        return grafo

    def salvar_lista_adj(self, arquivo_saida):
        # Salva a lista de adjacências em um arquivo de texto
        with open(arquivo_saida, 'w') as f:
            for rem, dests in self.lista_adj.items():
                arestas = " -> ".join(f"({d}, {p})" for d, p in dests.items())
                f.write(f"{rem}: {arestas}\n")

# Exemplo de uso
if __name__ == "__main__":
    # Caminho do dataset
    grafo = GrafoEmail.processar_diretorio("Amostra Enron - 2016")
    
    # Salva a lista de adjacências
    grafo.salvar_lista_adj("lista_emails.txt")
    
    # Informações gerais
    print(f"Vértices: {grafo.get_ordem()}")
    print(f"Arestas: {grafo.get_tamanho()}")
    print(f"Isolados: {grafo.get_isolados()}")
    
    # 20 maiores graus de saída
    print("\n20 maiores grau de saída:")
    for email, grau in grafo.get_20_grau_saida():
        print(f"{email}: {grau}")
        
    # 20 maiores graus de entrada
    print("\n20 maiores grau de entrada:")
    for email, grau in grafo.get_20_grau_entrada():
        print(f"{email}: {grau}")
    
    # Verificação de Euleriano
    resultado, condicoes = grafo.is_euleriano()
    if resultado:
        print("\nO grafo é Euleriano")
    else:
        print("\nO grafo não é Euleriano. Condições:")
        for condicao in condicoes:
            print(f"- {condicao}")

    # Exemplo de uso dos vértices até uma distância
    vertice_exemplo = next(iter(grafo.vertices), None)
    if vertice_exemplo:
        print(f"\nVértices até distância 2 de {vertice_exemplo}:")
        print(grafo.vertices_ate_distancia(vertice_exemplo, 2))

    # Cálculo do diâmetro
    print("\nCalculando diâmetro...")
    diametro, caminho = grafo.calcular_diametro()
    print(f"Diâmetro: {diametro}")
    print(f"Caminho correspondente: {' -> '.join(caminho)}")