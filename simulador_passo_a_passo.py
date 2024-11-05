from PyQt5.QtCore import QTimer

class Automato:
    # As outras funções permanecem iguais

    def gerar_grafo(self, caminho_imagem, caminho_atual=None):
        caminho_imagem_sem_extensao = os.path.splitext(caminho_imagem)[0]
        caminho_imagem_completo = os.path.abspath(caminho_imagem_sem_extensao)
        
        dot = graphviz.Digraph(format='png')
        dot.attr('node', shape='circle')

        for estado in self.estados.values():
            if estado.final:
                dot.node(estado.nome, shape='doublecircle')
            else:
                dot.node(estado.nome)

        # Marcar o caminho atual em destaque
        if caminho_atual:
            for (origem, simbolo, destino) in caminho_atual:
                dot.edge(origem, destino, label=simbolo, color="red", penwidth="2")
        
        # Transições normais
        for estado in self.estados.values():
            for simbolo, destino in estado.transicoes.items():
                if (estado.nome, simbolo, destino.nome) not in caminho_atual:
                    dot.edge(estado.nome, destino.nome, label=simbolo)

        # Estado inicial
        if self.estado_inicial:
            dot.node('', shape='none', label='')
            dot.edge('', self.estado_inicial.nome)

        dot.render(caminho_imagem_completo, cleanup=True)

    def simular_passo_a_passo(self, cadeia):
        estado_atual = self.estado_inicial
        self.passos = []
        for simbolo in cadeia:
            if simbolo in estado_atual.transicoes:
                estado_destino = estado_atual.transicoes[simbolo]
                self.passos.append((estado_atual.nome, simbolo, estado_destino.nome))
                estado_atual = estado_destino
            else:
                return False, self.passos  # Cadeia rejeitada
        return estado_atual.final, self.passos  # Aceitar ou rejeitar baseado no estado final

class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.automato = None
        self.timer = QTimer()
        self.initUI()

    def simular(self):
        if self.automato:
            cadeia = self.cadeia_entry.text()
            if cadeia:
                resultado, self.passos = self.automato.simular_passo_a_passo(cadeia)
                if resultado:
                    self.resultado_label.setText("Cadeia aceita! Simulação passo a passo iniciada.")
                else:
                    self.resultado_label.setText("Cadeia rejeitada! Simulação passo a passo iniciada.")
                
                # Iniciar a simulação passo a passo
                self.passo_atual = 0
                self.timer.timeout.connect(self.mostrar_passo)
                self.timer.start(1000)  # Intervalo de 1 segundo entre os passos
            else:
                self.resultado_label.setText("Insira uma cadeia para simulação.")
        else:
            self.resultado_label.setText("Crie um automato primeiro.")

    def mostrar_passo(self):
        if self.passo_atual < len(self.passos):
            origem, simbolo, destino = self.passos[self.passo_atual]
            caminho_imagem = "automato_passo.png"
            self.automato.gerar_grafo(caminho_imagem, caminho_atual=self.passos[:self.passo_atual+1])
            
            # Atualizar o label da imagem
            pixmap = QtGui.QPixmap(caminho_imagem)
            self.imagem_label.setPixmap(pixmap)
            self.resultado_label.setText(f"Passo {self.passo_atual + 1}: {origem} --{simbolo}--> {destino}")
            self.passo_atual += 1
        else:
            # Exibir o resultado final
            if self.resultado_final:
                self.resultado_label.setText("Cadeia aceita pelo autômato.")
            else:
                self.resultado_label.setText("Cadeia rejeitada pelo autômato.")
            
            # Parar o timer após todos os passos
            self.timer.stop()
