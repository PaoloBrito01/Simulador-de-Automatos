import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QFileDialog
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QFont
import json
import math

class Automato:
    def __init__(self):
        self.estados = set()
        self.transicoes = {}
        self.estado_atual = None
        self.estados_finais = set()

    def adicionar_transicao(self, origem, simbolo, destino):
        self.estados.add(origem)
        self.estados.add(destino)
        self.transicoes[(origem, simbolo)] = destino

    def definir_estado_inicial(self, estado):
        self.estado_atual = estado

    def definir_estados_finais(self, finais):
        self.estados_finais = set(finais)

    def proximo_estado(self, simbolo):
        if (self.estado_atual, simbolo) in self.transicoes:
            self.estado_atual = self.transicoes[(self.estado_atual, simbolo)]
            return self.estado_atual
        return None
    
    def salvar(self, nome_arquivo):
        # Salva o autômato em um arquivo JSON
        dados = {
            'estados': list(self.estados),
            'transicoes': {f"{origem},{simbolo}": destino for (origem, simbolo), destino in self.transicoes.items()},
            'estado_atual': self.estado_atual,
            'estados_finais': list(self.estados_finais),
        }
        with open(nome_arquivo, 'w') as f:
            json.dump(dados, f, indent=4)

    def carregar(self, nome_arquivo):
        # Carrega o autômato a partir de um arquivo JSON
        with open(nome_arquivo, 'r') as f:
            dados = json.load(f)
            self.estados = set(dados['estados'])
            self.transicoes = {
                (origem, simbolo): destino
                for transicao, destino in dados['transicoes'].items()
                for origem, simbolo in [transicao.split(',')]
            }
            self.estado_atual = dados['estado_atual']
            self.estados_finais = set(dados['estados_finais'])

class SimulatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuração e Simulação de Autômato")
        self.setGeometry(100, 100, 800, 600)

        # Layouts para configuração
        self.label = QLabel("Configuração do Autômato:", self)
        self.label.setAlignment(Qt.AlignCenter)
        
        # Campos de entrada para configuração
        self.input_estado_inicial = QLineEdit(self)
        self.input_estado_inicial.setPlaceholderText("Estado Inicial")
        
        self.input_estados_finais = QLineEdit(self)
        self.input_estados_finais.setPlaceholderText("Estados Finais (separados por vírgula)")
        
        self.input_transicao_origem = QLineEdit(self)
        self.input_transicao_origem.setPlaceholderText("Estado de Origem")
        
        self.input_transicao_simbolo = QLineEdit(self)
        self.input_transicao_simbolo.setPlaceholderText("Símbolo")
        
        self.input_transicao_destino = QLineEdit(self)
        self.input_transicao_destino.setPlaceholderText("Estado de Destino")
        
        self.botao_adicionar_transicao = QPushButton("Adicionar Transição", self)
        self.botao_adicionar_transicao.clicked.connect(self.adicionar_transicao)

        self.input_cadeia = QLineEdit(self)
        self.input_cadeia.setPlaceholderText("Digite a cadeia para simulação")

        self.start_button = QPushButton("Iniciar Simulação", self)
        self.start_button.clicked.connect(self.iniciar_simulacao)

        # Botões para salvar e carregar
        self.botao_salvar = QPushButton("Salvar Projeto", self)
        self.botao_salvar.clicked.connect(self.salvar_projeto)

        self.botao_carregar = QPushButton("Carregar Projeto", self)
        self.botao_carregar.clicked.connect(self.carregar_projeto)

        # Layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        
        # Layout para configurações do autômato
        layout_config = QHBoxLayout()
        layout_config.addWidget(self.input_estado_inicial)
        layout_config.addWidget(self.input_estados_finais)
        layout.addLayout(layout_config)
        
        layout_transicoes = QHBoxLayout()
        layout_transicoes.addWidget(self.input_transicao_origem)
        layout_transicoes.addWidget(self.input_transicao_simbolo)
        layout_transicoes.addWidget(self.input_transicao_destino)
        layout_transicoes.addWidget(self.botao_adicionar_transicao)
        layout.addLayout(layout_transicoes)
        
        layout.addWidget(self.input_cadeia)
        layout.addWidget(self.start_button)

        # Adicionar os botões ao layout
        layout.addWidget(self.botao_salvar)
        layout.addWidget(self.botao_carregar)

        self.setLayout(layout)

        # Timer para simulação
        self.timer = QTimer()
        self.timer.timeout.connect(self.proximo_passo)

        # Inicializar o autômato
        self.automato = Automato()
        self.cadeia = ""
        self.index = 0

    def adicionar_transicao(self):
        origem = self.input_transicao_origem.text()
        simbolo = self.input_transicao_simbolo.text()
        destino = self.input_transicao_destino.text()

        if origem and simbolo and destino:
            self.automato.adicionar_transicao(origem, simbolo, destino)
            self.label.setText(f"Transição adicionada: {origem} --{simbolo}--> {destino}")
        else:
            self.label.setText("Por favor, preencha todos os campos da transição.")

    def iniciar_simulacao(self):
        estado_inicial = self.input_estado_inicial.text()
        estados_finais = self.input_estados_finais.text().split(',')

        # Configurações iniciais
        if estado_inicial:
            self.automato.definir_estado_inicial(estado_inicial)
        self.automato.definir_estados_finais(estados_finais)
        
        # Obter a cadeia do campo de entrada
        self.cadeia = self.input_cadeia.text()
        
        # Resetar o índice e iniciar a simulação
        if self.cadeia:
            self.index = 0
            self.label.setText("Simulação em andamento...")
            self.timer.start(1000)  # Intervalo de 1 segundo
        else:
            self.label.setText("Por favor, insira uma cadeia válida.")

    def proximo_passo(self):
        if self.index < len(self.cadeia):
            simbolo = self.cadeia[self.index]
            novo_estado = self.automato.proximo_estado(simbolo)
            self.index += 1

            if novo_estado:
                self.label.setText(f"Estado atual: {novo_estado}")
                self.update()
            else:
                self.label.setText("Cadeia rejeitada.")
                self.timer.stop()
        else:
            if self.automato.estado_atual in self.automato.estados_finais:
                self.label.setText("Cadeia aceita!")
            else:
                self.label.setText("Cadeia rejeitada.")
            self.timer.stop()
    
    def salvar_projeto(self):
        nome_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Projeto", "", "Arquivos JSON (*.json)")
        if nome_arquivo:
            self.automato.salvar(nome_arquivo)

    def carregar_projeto(self):
        nome_arquivo, _ = QFileDialog.getOpenFileName(self, "Carregar Projeto", "", "Arquivos JSON (*.json)")
        if nome_arquivo:
            self.automato.carregar(nome_arquivo)
            # Atualizar a interface após carregar o projeto
            self.atualizar_interface()

    def atualizar_interface(self):
        self.input_estado_inicial.setText(self.automato.estado_atual if self.automato.estado_atual else "")
        self.input_estados_finais.setText(', '.join(self.automato.estados_finais))
        self.input_transicao_origem.clear()
        self.input_transicao_simbolo.clear()
        self.input_transicao_destino.clear()
        self.input_cadeia.clear()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        qp.setFont(QFont("Arial", 10))
        center_x, center_y = 400, 300  # Centro do círculo
        radius = 200  # Raio do círculo

        # Distribuir estados em um círculo
        estados_pos = {}
        num_estados = len(self.automato.estados)
        angle_step = 2 * math.pi / num_estados if num_estados > 0 else 0
        for i, estado in enumerate(self.automato.estados):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            estados_pos[estado] = QPointF(x, y)

        # Desenhar estados
        for estado, pos in estados_pos.items():
            if estado == self.automato.estado_atual:
                qp.setBrush(Qt.green)  # Estado atual em verde
            elif estado in self.automato.estados_finais:
                qp.setBrush(Qt.red)  # Estado final em vermelho
            else:
                qp.setBrush(Qt.white)  # Outros estados em branco
            qp.drawEllipse(pos, 20, 20)
            qp.drawText(pos.x(), pos.y(), estado)

        # Desenhar transições
        curve_count = {}
        for (origem, simbolo), destino in self.automato.transicoes.items():
            origem_pos = estados_pos[origem]
            destino_pos = estados_pos[destino]
            qp.drawLine(origem_pos, destino_pos)

            # Calcular o ponto médio para a curva
            mid_x = (origem_pos.x() + destino_pos.x()) / 2
            mid_y = (origem_pos.y() + destino_pos.y()) / 2

            # Desenhar a curva
            if (origem, destino) not in curve_count:
                curve_count[(origem, destino)] = 0
            curve_count[(origem, destino)] += 1

            # Adicionar um deslocamento vertical para cada curva entre os mesmos estados
            offset = (curve_count[(origem, destino)] - 1) * 10
            qp.drawText(mid_x, mid_y + offset, simbolo)

        qp.end()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulatorApp()
    window.show()
    sys.exit(app.exec_())
