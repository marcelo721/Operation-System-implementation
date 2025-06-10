import threading
import tkinter as tk
import random
import time

class MonitorBuffer:
    def __init__(self, capacidade, gui_callback, log_callback):
        self.buffer = []
        self.capacidade = capacidade
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        self.gui_callback = gui_callback
        self.log_callback = log_callback

    def inserir(self, item):
        with self.not_full:
            while len(self.buffer) >= self.capacidade:
                self.log_callback("Buffer cheio. Produtor esperando...")
                self.not_full.wait()
            self.buffer.append(item)
            self.gui_callback(self.buffer)
            self.log_callback(f"Item produzido: {item}")
            self.not_empty.notify()

    def remover(self):
        with self.not_empty:
            while len(self.buffer) == 0:
                self.log_callback("Buffer vazio. Consumidor esperando...")
                self.not_empty.wait()
            item = self.buffer.pop(0)
            self.gui_callback(self.buffer)
            self.log_callback(f"Item consumido: {item}")
            self.not_full.notify()
            return item

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulação de Monitor - Produtor/Consumidor")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        # Título
        tk.Label(root, text="Monitor: Produtor x Consumidor", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        # Exibição do buffer
        tk.Label(root, text="Buffer atual:", font=("Arial", 12), bg="#f0f0f0").pack()
        self.buffer_display = tk.Label(root, text="[]", font=("Courier", 16), bg="white", width=40, height=2, relief="sunken")
        self.buffer_display.pack(pady=5)

        # Status
        self.status_label = tk.Label(root, text="", font=("Arial", 12), bg="#f0f0f0", fg="blue")
        self.status_label.pack(pady=5)

        # Área de logs
        tk.Label(root, text="Logs:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
        self.log_text = tk.Text(root, height=10, width=70, font=("Courier", 10))
        self.log_text.pack(pady=5)
        self.log_text.config(state="disabled")

        # Botão de início
        self.botao_iniciar = tk.Button(root, text="Iniciar Simulação", font=("Arial", 12), command=self.iniciar_simulacao)
        self.botao_iniciar.pack(pady=10)

        # Cria monitor, mas ainda não inicia threads
        self.buffer = MonitorBuffer(capacidade=5, gui_callback=self.atualizar_interface, log_callback=self.adicionar_log)
        self.threads_iniciadas = False

    def atualizar_interface(self, buffer):
        self.buffer_display.config(text=str(buffer))

    def adicionar_log(self, mensagem):
        self.log_text.config(state="normal")
        self.log_text.insert("end", mensagem + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def iniciar_simulacao(self):
        if not self.threads_iniciadas:
            self.threads_iniciadas = True
            produtor = threading.Thread(target=self.executar_produtor)
            consumidor = threading.Thread(target=self.executar_consumidor)
            produtor.daemon = True
            consumidor.daemon = True
            produtor.start()
            consumidor.start()
            self.status_label.config(text="Simulação em andamento...")

    #Produtor
    def executar_produtor(self):
        while True:
            item = random.randint(1, 100)
            self.status_label.config(text=f"Produzindo: {item}")
            self.buffer.inserir(item)
            time.sleep(random.uniform(0.5, 2))
    #consumidor
    def executar_consumidor(self):
        while True:
            item = self.buffer.remover()
            self.status_label.config(text=f"Consumindo: {item}")
            time.sleep(random.uniform(1, 2))

## MAIN
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
