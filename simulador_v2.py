import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QFileDialog
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QFont
from PyQt5.QtWidgets import QCheckBox
import math

class Automato:
    def __init__(self):
        self.estados = set()
        self.transicoes = {}  # Transições agora vão armazenar múltiplos destinos
        self.estado_atual = None
        self.estados_finais = set()
        self.estado_inicial_configurado = None  # Armazena o estado inicial configurado

    def adicionar_transicao(self, origem, simbolo, destino):
        """Adiciona uma transição do estado 'origem' para o estado 'destino' usando o 'simbolo'.
        Se simbolo for '%', é uma transição em vazio."""
        self.estados.add(origem)
        self.estados.add(destino)
        
        chave = (origem, simbolo)  # A chave da transição inclui o símbolo
        if chave not in self.transicoes:
            self.transicoes[chave] = set()
        self.transicoes[chave].add(destino)

    def definir_estado_inicial(self, estado):
        self.estado_atual = estado
        self.estado_inicial_configurado = estado 

    def definir_estados_finais(self, finais):
        self.estados_finais = set(finais)

    def proximo_estado(self, simbolo):
        """Para AFN com transições em vazio (`%` ou `ε`), devolve todos os estados possíveis, incluindo os alcançados por transições em vazio."""
        estados_possiveis = set()
        estados_a_processar = {self.estado_atual}

        while estados_a_processar:
            estado_atual = estados_a_processar.pop()

            # Verifica transições com o símbolo fornecido
            chave_simbolo = (estado_atual, simbolo)
            if chave_simbolo in self.transicoes:
                estados_possiveis.update(self.transicoes[chave_simbolo])

            # Verifica transições em vazio (`%`)
            chave_epsilon = (estado_atual, '%')
            if chave_epsilon in self.transicoes:
                for novo_estado in self.transicoes[chave_epsilon]:
                    if novo_estado not in estados_possiveis:
                        estados_a_processar.add(novo_estado)

        return estados_possiveis



    def iniciar_simulacao(self):
        self.cadeia = self.input_cadeia.text().strip()
        self.index = 0
        self.automato.definir_estado_inicial(self.automato.estado_inicial_configurado)
        self.timer.start(1000)  # Intervalo de 1 segundo entre cada passo da simulação
        self.proximo_passo()  # Executa o primeiro passo imediatamente

    def proximo_passo(self):
        if self.index < len(self.cadeia):
            simbolo = self.cadeia[self.index]
            estados_possiveis = self.automato.proximo_estado(simbolo)

            if estados_possiveis:
                self.automato.estado_atual = list(estados_possiveis)[0]  # Escolhe um estado arbitrariamente
                self.index += 1
            else:
                self.timer.stop()
                self.label.setText("Cadeia rejeitada!")
                return
        else:
            # Processa transições em vazio após consumir toda a cadeia
            estados_possiveis = self.automato.proximo_estado('%')
            if not estados_possiveis:
                self.timer.stop()
                if self.automato.estado_atual in self.automato.estados_finais:
                    self.label.setText("Cadeia aceita!")
                else:
                    self.label.setText("Cadeia rejeitada!")
                return

        # Continua a simulação para o próximo passo
        self.timer.start(1000)

                
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
        self.input_transicao_epsilon = QCheckBox("Transição em Vazio (ε)", self)
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
        self.cadeia = "%"
        self.index = 0

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
        if self.cadeia == "":  # Cadeia vazia
            self.index = 0
            self.label.setText("Simulação em andamento para cadeia vazia...")
            self.timer.start(1000)  # Intervalo de 1 segundo
        elif self.cadeia:  # Cadeia não vazia
            self.index = 0
            self.label.setText("Simulação em andamento...")
            self.timer.start(1000)  # Intervalo de 1 segundo
        else:
            self.label.setText("Por favor, insira uma cadeia válida.")



    def adicionar_transicao(self):
        origem = self.input_transicao_origem.text().strip()
        simbolo = self.input_transicao_simbolo.text().strip()
        destino = self.input_transicao_destino.text().strip()

        if origem and destino:  # Permite o campo 'simbolo' vazio
            # Se o símbolo estiver vazio, tratamos como transição em vazio
            simbolo = '%' if not simbolo else simbolo  
            self.automato.adicionar_transicao(origem, simbolo, destino)
            if simbolo == '%':
                self.label.setText(f"Transição adicionada: {origem} --ε--> {destino}")
            else:
                self.label.setText(f"Transição adicionada: {origem} --{simbolo}--> {destino}")
        else:
            self.label.setText("Por favor, preencha os campos de origem e destino.")

    def simular_cadeia(self, cadeia):
        estados_atuais = {self.automato.estado_inicial_configurado}
        indice_cadeia = 0

        while indice_cadeia <= len(cadeia):
            novos_estados = set()
            for estado in estados_atuais:
                # Processar transições em vazio
                if (estado, '%') in self.automato.transicoes:
                    novos_estados.update(self.automato.transicoes[(estado, '%')])

                # Processar transições com o símbolo atual (se houver)
                if indice_cadeia < len(cadeia):
                    simbolo_atual = cadeia[indice_cadeia]
                    if (estado, simbolo_atual) in self.automato.transicoes:
                        novos_estados.update(self.automato.transicoes[(estado, simbolo_atual)])

            estados_atuais = novos_estados

            # Avançar o índice apenas se um símbolo da cadeia for consumido
            if indice_cadeia < len(cadeia) and any(
                (estado, cadeia[indice_cadeia]) in self.automato.transicoes for estado in estados_atuais
            ):
                indice_cadeia += 1

            if not estados_atuais:
                break

        if any(estado in self.automato.estados_finais for estado in estados_atuais):
            return True  # Cadeia aceita
        else:
            return False  # Cadeia rejeitada

        
    def proximo_estado(self, simbolo):
        """Para AFN com transições ε, devolve todos os estados possíveis, incluindo os alcançados por ε-transições."""
        estados_possiveis = set()
        estados_a_processar = {self.estado_atual}

        while estados_a_processar:
            estado_atual = estados_a_processar.pop()
            
            # Verifica transições com o símbolo fornecido ou transições ε
            chave_simbolo = (estado_atual, simbolo)
            chave_epsilon = (estado_atual, 'ε')

            # Adiciona os estados alcançados pela transição com símbolo
            if chave_simbolo in self.transicoes:
                estados_possiveis.update(self.transicoes[chave_simbolo])
            
            # Adiciona os estados alcançados por transições ε
            if chave_epsilon in self.transicoes:
                for novo_estado in self.transicoes[chave_epsilon]:
                    if novo_estado not in estados_possiveis:
                        estados_a_processar.add(novo_estado)

        return estados_possiveis

    
def salvar_projeto(self):
    nome_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Projeto", "", "Arquivos de Texto (*.txt)")
    if not nome_arquivo.endswith(".txt"):
        nome_arquivo += ".txt"
    
    if nome_arquivo:
        with open(nome_arquivo, 'w') as f:
            # Salvar estados
            f.write("#states\n")
            for estado in self.automato.estados:
                f.write(f"{estado}\n")
            
            # Salvar estado inicial
            f.write("#initial\n")
            f.write(f"{self.automato.estado_inicial_configurado}\n")  # Use o estado inicial configurado
            
            # Salvar estados finais
            f.write("#accepting\n")
            if self.automato.estados_finais:
                f.write("\n".join(self.automato.estados_finais) + "\n")
            
            # Salvar alfabeto
            f.write("#alphabet\n")
            alfabeto = {simbolo for (_, simbolo) in self.automato.transicoes.keys()}
            for simbolo in alfabeto:
                f.write(f"{'%' if simbolo == '%' else simbolo}\n")  # Salvar '%' para transições em vazio
            
            # Salvar transições
            f.write("#transitions\n")
            for (origem, simbolo), destinos in self.automato.transicoes.items():
                for destino in destinos:
                    f.write(f"{origem}:{'%' if simbolo == '%' else simbolo}>{destino}\n")

def carregar_projeto(self):
    nome_arquivo, _ = QFileDialog.getOpenFileName(self, "Carregar Projeto", "", "Arquivos de Texto (*.txt)")
    if nome_arquivo:
        try:
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                lines = f.readlines()

                # Limpar espaços e quebras de linha extras
                lines = [line.strip() for line in lines if line.strip()]

                # Iniciar variáveis
                estados = set()
                transicoes = {}
                estado_inicial = None
                estados_finais = set()
                alfabeto = set()

                # Processar as linhas
                section = None
                for line in lines:
                    if line.startswith("#"):
                        section = line[1:].strip()  # Pega a seção após o #
                    else:
                        if section == "states":
                            estados.add(line)
                        elif section == "initial":
                            estado_inicial = line
                        elif section == "accepting":
                            if line:
                                estados_finais.add(line)
                        elif section == "alphabet":
                            alfabeto.add('%' if line == '%' else line)
                        elif section == "transitions":
                            origem, resto = line.split(":")
                            simbolo, destino = resto.split(">")
                            transicoes[(origem, '%' if simbolo == '%' else simbolo)] = destino

                # Carregar no autômato
                self.automato.estados = estados
                self.automato.estado_atual = estado_inicial
                self.automato.estados_finais = estados_finais
                for (origem, simbolo), destino in transicoes.items():
                    self.automato.adicionar_transicao(origem, simbolo if simbolo != '%' else 'ε', destino)

                self.atualizar_interface()

        except Exception as e:
            print(f"Erro ao carregar o autômato: {e}")

    def paintEvent(self):
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
            else:
                qp.setBrush(Qt.white)  # Outros estados em branco

            # Desenhar o círculo principal
            qp.drawEllipse(pos, 20, 20)

            # Desenhar círculo interno para estados finais
            if estado in self.automato.estados_finais:
                qp.setBrush(Qt.NoBrush)  # Não preencher o círculo interno
                qp.drawEllipse(pos - QPointF(5, 5), 30, 30)  # Círculo maior

            # Adicionar texto do estado
            qp.setBrush(Qt.NoBrush)  # Sem preenchimento para texto
            qp.drawText(int(pos.x() - 10), int(pos.y() + 5), estado)

        # Desenhar transições com deslocamento
        processed_transitions = {}  # Rastreamento de transições já desenhadas
        for (origem, simbolo), destinos in self.automato.transicoes.items():
            for destino in destinos:
                origem_pos = estados_pos[origem]
                destino_pos = estados_pos[destino]

                # Deslocamento baseado em transições duplicadas
                key = (origem, destino)
                if key not in processed_transitions:
                    processed_transitions[key] = 0
                offset = 20 * processed_transitions[key]  # Incremento para transições sobrepostas
                processed_transitions[key] += 1

                # Adicionar deslocamento para evitar sobreposição
                mid_x = (origem_pos.x() + destino_pos.x()) / 2
                mid_y = (origem_pos.y() + destino_pos.y()) / 2
                if origem != destino:
                    mid_x += offset
                    mid_y += offset
                else:
                    # Desenhar loops com curva
                    qp.drawEllipse(origem_pos.x() - 30, origem_pos.y() - 60, 60, 40)

                # Linha da transição (ajustada para loops e deslocamento)
                if origem != destino:
                    qp.drawLine(origem_pos, destino_pos)

                # Desenhar símbolo próximo ao meio da linha ou na curva
                simbolo_texto = "(ε)" if simbolo == 'ε' else simbolo
                qp.drawText(int(mid_x), int(mid_y), simbolo_texto)

                # Desenhar seta para indicar a direção
                if origem != destino:
                    line = QPointF(destino_pos.x() - origem_pos.x(), destino_pos.y() - origem_pos.y())
                    angle = math.atan2(line.y(), line.x())
                    end_x = destino_pos.x() - 20 * math.cos(angle)
                    end_y = destino_pos.y() - 20 * math.sin(angle)
                    arrow_size = 10
                    arrow_angle = math.pi / 6
                    arrow_x1 = end_x - arrow_size * math.cos(angle - arrow_angle)
                    arrow_y1 = end_y - arrow_size * math.sin(angle - arrow_angle)
                    arrow_x2 = end_x - arrow_size * math.cos(angle + arrow_angle)
                    arrow_y2 = end_y - arrow_size * math.sin(angle + arrow_angle)
                    qp.drawPolygon(QPointF(end_x, end_y), QPointF(arrow_x1, arrow_y1), QPointF(arrow_x2, arrow_y2))

        qp.end()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulatorApp()
    window.show()
    sys.exit(app.exec_())

