import sys
import os
import json
import graphviz
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer


# Classe para representar um estado do autômato
class Estado:
    def __init__(self, nome, final=False):
        self.nome = nome
        self.final = final
        self.transicoes = {}  # { símbolo: estado }

# Classe para representar um autômato
class Automato:
    def __init__(self, nome):
        self.nome = nome
        self.estados = {}
        self.estado_inicial = None

    def adicionar_estado(self, nome, final=False):
        estado = Estado(nome, final)
        self.estados[nome] = estado
        if self.estado_inicial is None:
            self.estado_inicial = estado

    def adicionar_transicao(self, origem, simbolo, destino):
        if origem in self.estados and destino in self.estados:
            self.estados[origem].transicoes[simbolo] = self.estados[destino]
        else:
            raise ValueError("Estado de origem ou destino não existe.")

    def simular(self, cadeia):
        estado_atual = self.estado_inicial
        for simbolo in cadeia:
            if simbolo in estado_atual.transicoes:
                estado_atual = estado_atual.transicoes[simbolo]
            else:
                return False  # Cadeia rejeitada
        return estado_atual.final  # Aceitar ou rejeitar baseado no estado final

    def salvar(self, caminho):
        dados = {
            'nome': self.nome,
            'estados': {}
        }
        for estado in self.estados.values():
            dados['estados'][estado.nome] = {
                'final': estado.final,
                'transicoes': {simbolo: destino.nome for simbolo, destino in estado.transicoes.items()}
            }
        with open(caminho, 'w') as f:
            json.dump(dados, f, indent=4)

    @classmethod
    def carregar(cls, caminho):
        with open(caminho, 'r') as f:
            dados = json.load(f)
            automato = cls(dados['nome'])
            for nome, info in dados['estados'].items():
                automato.adicionar_estado(nome, info['final'])
            for nome, info in dados['estados'].items():
                for simbolo, destino in info['transicoes'].items():
                    automato.adicionar_transicao(nome, simbolo, destino)
            return automato

    def gerar_grafo(self, caminho_imagem):
        # Remove a extensão, pois graphviz vai adicionar automaticamente
        caminho_imagem_sem_extensao = os.path.splitext(caminho_imagem)[0]
        caminho_imagem_completo = os.path.abspath(caminho_imagem_sem_extensao)
        
        dot = graphviz.Digraph(format='png')
        dot.attr('node', shape='circle')

        for estado in self.estados.values():
            if estado.final:
                dot.node(estado.nome, shape='doublecircle')
            else:
                dot.node(estado.nome)

        for estado in self.estados.values():
            for simbolo, destino in estado.transicoes.items():
                dot.edge(estado.nome, destino.nome, label=simbolo)

        # Estado inicial
        if self.estado_inicial:
            dot.node('', shape='none', label='')
            dot.edge('', self.estado_inicial.nome)

        # Renderizar o gráfico
        dot.render(caminho_imagem_completo, cleanup=True)
        
        # Verificar se a imagem foi criada com sucesso
        caminho_imagem_final = caminho_imagem_completo + '.png'
        if not os.path.exists(caminho_imagem_final):
            raise FileNotFoundError(f"A imagem não foi criada no caminho: {caminho_imagem_final}")
        
    def simular_passo(self, cadeia):
        estado_atual = self.estado_inicial
        self.passos = []
        for simbolo in cadeia:
            if simbolo in estado_atual.transicoes:
                estado_destino = estado_atual.transicoes[simbolo]
                self.passos.append((estado_atual.nome, simbolo, estado_destino.nome))
                estado_atual = estado_destino
            else:
                # Caso cadeia rejeitada
                return False, self.passos 
        return estado_atual.final, self.passos  # Aceitar ou rejeitar baseado no estado final



# Classe para a interface gráfica com PyQt5
class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.automato = None
        self.initUI()

    def initUI(self):
        # Configurações da janela
        self.setWindowTitle("Simulador de Autômatos Finitos")
        self.setGeometry(100, 100, 800, 600)
        # Layout principal
        layout = QtWidgets.QVBoxLayout()
        # Grupo de criação de autômato
        self.criar_automato_group = QtWidgets.QGroupBox("Criar Automato")
        criar_automato_layout = QtWidgets.QHBoxLayout()
        self.nome_automato_entry = QtWidgets.QLineEdit()
        self.nome_automato_entry.setPlaceholderText("Nome do autômato")
        self.criar_automato_button = QtWidgets.QPushButton("Criar Automato")
        self.criar_automato_button.clicked.connect(self.criar_automato)
        criar_automato_layout.addWidget(self.nome_automato_entry)
        criar_automato_layout.addWidget(self.criar_automato_button)
        self.criar_automato_group.setLayout(criar_automato_layout)
        layout.addWidget(self.criar_automato_group)
        # Grupo de adição de estado
        self.estado_group = QtWidgets.QGroupBox("Adicionar Estado")
        estado_layout = QtWidgets.QHBoxLayout()
        self.estado_nome_entry = QtWidgets.QLineEdit()
        self.estado_nome_entry.setPlaceholderText("Nome do estado")
        self.estado_final_checkbox = QtWidgets.QCheckBox("É estado final")
        self.adicionar_estado_button = QtWidgets.QPushButton("Adicionar Estado")
        self.adicionar_estado_button.clicked.connect(self.adicionar_estado)
        estado_layout.addWidget(self.estado_nome_entry)
        estado_layout.addWidget(self.estado_final_checkbox)
        estado_layout.addWidget(self.adicionar_estado_button)
        self.estado_group.setLayout(estado_layout)
        layout.addWidget(self.estado_group)
        # Grupo de adição de transição
        self.transicao_group = QtWidgets.QGroupBox("Adicionar Transição")
        transicao_layout = QtWidgets.QHBoxLayout()
        self.origem_entry = QtWidgets.QLineEdit()
        self.origem_entry.setPlaceholderText("Estado de origem")
        self.simbolo_entry = QtWidgets.QLineEdit()
        self.simbolo_entry.setPlaceholderText("Símbolo")
        self.destino_entry = QtWidgets.QLineEdit()
        self.destino_entry.setPlaceholderText("Estado de destino")
        self.adicionar_transicao_button = QtWidgets.QPushButton("Adicionar Transição")
        self.adicionar_transicao_button.clicked.connect(self.adicionar_transicao)
        transicao_layout.addWidget(self.origem_entry)
        transicao_layout.addWidget(self.simbolo_entry)
        transicao_layout.addWidget(self.destino_entry)
        transicao_layout.addWidget(self.adicionar_transicao_button)
        self.transicao_group.setLayout(transicao_layout)
        layout.addWidget(self.transicao_group)
        # Grupo de simulação de cadeia
        self.cadeia_group = QtWidgets.QGroupBox("Simular Cadeia")
        cadeia_layout = QtWidgets.QHBoxLayout()
        self.cadeia_entry = QtWidgets.QLineEdit()
        self.cadeia_entry.setPlaceholderText("Cadeia a ser testada")
        self.simular_button = QtWidgets.QPushButton("Simular")
        self.simular_button.clicked.connect(self.simular)
        cadeia_layout.addWidget(self.cadeia_entry)
        cadeia_layout.addWidget(self.simular_button)
        self.cadeia_group.setLayout(cadeia_layout)
        layout.addWidget(self.cadeia_group)

        # Exibição do resultado
        self.resultado_label = QtWidgets.QLabel("")
        self.resultado_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.resultado_label)

        # Exibição da imagem do automato
        self.imagem_label = QtWidgets.QLabel("Imagem do autômato aparecerá aqui")
        self.imagem_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.imagem_label)

        # Grupo de gerenciamento de automatos (Salvar/Carregar)
        self.gerenciar_group = QtWidgets.QGroupBox("Gerenciar Autômatos")
        gerenciar_layout = QtWidgets.QHBoxLayout()
        self.salvar_button = QtWidgets.QPushButton("Salvar Automato")
        self.salvar_button.clicked.connect(self.salvar_automato)
        self.carregar_button = QtWidgets.QPushButton("Carregar Automato")
        self.carregar_button.clicked.connect(self.carregar_automato)
        self.exibir_grafo_button = QtWidgets.QPushButton("Exibir Automato")
        self.exibir_grafo_button.clicked.connect(self.exibir_grafo)
        gerenciar_layout.addWidget(self.salvar_button)
        gerenciar_layout.addWidget(self.carregar_button)
        gerenciar_layout.addWidget(self.exibir_grafo_button)
        self.gerenciar_group.setLayout(gerenciar_layout)
        layout.addWidget(self.gerenciar_group)
        # Definindo o layout da janela
        self.setLayout(layout)

    def criar_automato(self):
        nome = self.nome_automato_entry.text()
        if nome:
            self.automato = Automato(nome)
            self.resultado_label.setText(f"Automato '{nome}' criado com sucesso!")
        else:
            self.resultado_label.setText("Insira um nome válido para o autômato.")

    def adicionar_estado(self):
        if self.automato:
            nome = self.estado_nome_entry.text()
            final = self.estado_final_checkbox.isChecked()
            if nome:
                self.automato.adicionar_estado(nome, final)
                self.resultado_label.setText(f"Estado '{nome}' adicionado com sucesso!")
            else:
                self.resultado_label.setText("Insira um nome válido para o estado.")
        else:
            self.resultado_label.setText("Crie um automato primeiro.")

    def adicionar_transicao(self):
        if self.automato:
            origem = self.origem_entry.text()
            simbolo = self.simbolo_entry.text()
            destino = self.destino_entry.text()
            if origem and simbolo and destino:
                try:
                    self.automato.adicionar_transicao(origem, simbolo, destino)
                    self.resultado_label.setText(f"Transição adicionada: {origem} --{simbolo}--> {destino}")
                except ValueError as e:
                    self.resultado_label.setText(str(e))
            else:
                self.resultado_label.setText("Preencha todos os campos para a transição.")
        else:
            self.resultado_label.setText("Crie um automato primeiro.")
    
    def simular(self):
        if self.automato:
            cadeia = self.cadeia_entry.text()
            if cadeia:
                resultado = self.automato.simular(cadeia)
                if resultado:
                    self.resultado_label.setText(f"A cadeia '{cadeia}' foi aceita pelo autômato.")
                else:
                    self.resultado_label.setText(f"A cadeia '{cadeia}' foi rejeitada pelo autômato.")
            else:
                self.resultado_label.setText("Insira uma cadeia para simulação.")
        else:
            self.resultado_label.setText("Crie um automato primeiro.")
    
    #### Função teste para simular a execução do autômato ##############
    #def simular(self):


    def mostrar_passo(self):
        if self.passo_atual < len(self.passos):
            estado_nome, simbolo = self.passos[self.passo_atual]
            self.resultado_label.setText(f"Passo {self.passo_atual + 1}: Estado '{estado_nome}', Símbolo: '{simbolo}'")
            self.passo_atual += 1
        else:
            # Exibe o resultado final após a última transição
            if self.resultado_final:
                self.resultado_label.setText("Cadeia aceita pelo autômato.")
            else:
                self.resultado_label.setText("Cadeia rejeitada pelo autômato.")
            
            # Para o timer após mostrar todos os passos
            self.timer.stop()



    def salvar_automato(self):
        if self.automato:
            caminho, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar Automato", "", "JSON Files (*.json)")
            if caminho:
                self.automato.salvar(caminho)
                self.resultado_label.setText(f"Automato salvo em {caminho}.")
        else:
            self.resultado_label.setText("Crie ou carregue um automato primeiro.")

    def carregar_automato(self):
        caminho, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Carregar Automato", "", "JSON Files (*.json)")
        if caminho:
            self.automato = Automato.carregar(caminho)
            self.resultado_label.setText(f"Automato '{self.automato.nome}' carregado com sucesso!")

    def exibir_grafo(self):
        if self.automato:
            caminho_imagem = "automato.png"
            try:
                self.automato.gerar_grafo(caminho_imagem)
                
                # Forçar o carregamento da imagem e atualizar a QLabel
                pixmap = QtGui.QPixmap()
                pixmap.load(caminho_imagem)  # Usar load em vez de atribuir diretamente
                if pixmap.isNull():
                    self.resultado_label.setText("Erro ao carregar a imagem do autômato.")
                else:
                    self.imagem_label.setPixmap(pixmap)
                    self.imagem_label.repaint()  # Forçar atualização da QLabel
                    self.resultado_label.setText("Imagem do autômato gerada com sucesso.")
            except FileNotFoundError as e:
                self.resultado_label.setText(str(e))
            except Exception as e:
                self.resultado_label.setText(f"Erro: {str(e)}")
        else:
            self.resultado_label.setText("Crie ou carregue um automato primeiro.")



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())