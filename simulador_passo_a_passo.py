import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor

class Automato:
    # Implementação do autômato com transições e estados (simples para exemplo)
    def __init__(self, estados, transicoes, estado_inicial, estados_finais):
        self.estados = estados
        self.transicoes = transicoes
        self.estado_atual = estado_inicial
        self.estados_finais = estados_finais

    def proximo_estado(self, simbolo):
        if (self.estado_atual, simbolo) in self.transicoes:
            self.estado_atual = self.transicoes[(self.estado_atual, simbolo)]
            return self.estado_atual
        return None

class SimulatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulação Passo-a-Passo do Autômato")
        self.setGeometry(100, 100, 600, 400)

        # Layout
        self.label = QLabel("Clique em 'Iniciar' para começar a simulação.", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.start_button = QPushButton("Iniciar", self)
        self.start_button.clicked.connect(self.iniciar_simulacao)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        self.setLayout(layout)

        # Timer para simulação passo-a-passo
        self.timer = QTimer()
        self.timer.timeout.connect(self.proximo_passo)

        # Configuração do autômato (exemplo)
        estados = {"q0", "q1", "q2"}
        transicoes = {
            ("q0", "a"): "q1",
            ("q1", "b"): "q2"
        }
        self.automato = Automato(estados, transicoes, "q0", {"q2"})
        self.cadeia = "ab"
        self.index = 0

    def iniciar_simulacao(self):
        self.automato.estado_atual = "q0"  # Reset do estado inicial
        self.index = 0  # Reset do índice da cadeia
        self.label.setText("Simulação em andamento...")
        self.timer.start(1000)  # Iniciar timer com intervalo de 1 segundo

    def proximo_passo(self):
        if self.index < len(self.cadeia):
            simbolo = self.cadeia[self.index]
            novo_estado = self.automato.proximo_estado(simbolo)
            self.index += 1

            if novo_estado:
                self.label.setText(f"Estado atual: {novo_estado}")
                self.update()  # Atualizar interface gráfica para refletir novo estado
            else:
                self.label.setText("Cadeia rejeitada.")
                self.timer.stop()
        else:
            # Verifica se o estado final é de aceitação
            if self.automato.estado_atual in self.automato.estados_finais:
                self.label.setText("Cadeia aceita!")
            else:
                self.label.setText("Cadeia rejeitada.")
            self.timer.stop()

    def paintEvent(self, event):
        # Método para desenhar os estados e transições do autômato
        qp = QPainter()
        qp.begin(self)

        # Desenhar estados (círculos) com destaque para o estado atual
        estados_pos = {"q0": (100, 200), "q1": (300, 200), "q2": (500, 200)}
        for estado, pos in estados_pos.items():
            if estado == self.automato.estado_atual:
                qp.setBrush(QBrush(QColor("red")))  # Estado atual destacado em vermelho
            else:
                qp.setBrush(QBrush(QColor("lightgray")))
            qp.drawEllipse(pos[0], pos[1], 50, 50)
            qp.drawText(pos[0] + 20, pos[1] + 30, estado)

        # Desenhar transições (linhas com setas)
        qp.setPen(QPen(Qt.black, 2))
        qp.drawLine(150, 225, 300, 225)  # Transição q0 -> q1
        qp.drawLine(350, 225, 500, 225)  # Transição q1 -> q2

        qp.end()

app = QApplication(sys.argv)
simulator_app = SimulatorApp()
simulator_app.show()
sys.exit(app.exec_())
