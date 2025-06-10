import tkinter as tk
import threading
import time
import random
from queue import Queue, Empty

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Troca de Mensagens - Produtor/Consumidor")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        self.msg_queue = Queue()  # fila de troca de mensagens

        # Título
        tk.Label(root, text="Troca de Mensagens", font=("Arial", 16, "bold"), bg="#f0f0f0").pack(pady=10)

        # Fila visual
        tk.Label(root, text="Fila de Mensagens:", font=("Arial", 12), bg="#f0f0f0").pack()
        self.queue_display = tk.Label(root, text="[]", font=("Courier", 16), bg="white", width=40, height=2, relief="sunken")
        self.queue_display.pack(pady=5)

        # Status
        self.status_label = tk.Label(root, text="", font=("Arial", 12), bg="#f0f0f0", fg="blue")
        self.status_label.pack(pady=5)

        # Área de log
        tk.Label(root, text="Logs:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack()
        self.log_text = tk.Text(root, height=10, width=70, font=("Courier", 10))
        self.log_text.pack(pady=5)
        self.log_text.config(state="disabled")

        # Botão para iniciar
        self.start_button = tk.Button(root, text="Iniciar Simulação", font=("Arial", 12), command=self.iniciar_simulacao)
        self.start_button.pack(pady=10)

        self.executando = False

    def atualizar_interface(self):
        try:
            elementos = list(self.msg_queue.queue)
            self.queue_display.config(text=str(elementos))
        except:
            pass

    def adicionar_log(self, mensagem):
        self.log_text.config(state="normal")
        self.log_text.insert("end", mensagem + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def iniciar_simulacao(self):
        if not self.executando:
            self.executando = True
            threading.Thread(target=self.produtor, daemon=True).start()
            threading.Thread(target=self.consumidor, daemon=True).start()
            self.status_label.config(text="Simulação em andamento...")

    def produtor(self):
        while self.executando:
            msg = random.randint(100, 999)
            self.msg_queue.put(msg)
            self.adicionar_log(f"Produtor -> enviou: {msg}")
            self.atualizar_interface()
            time.sleep(random.uniform(0.5, 2))

    def consumidor(self):
        while self.executando:
            try:
                msg = self.msg_queue.get(timeout=1)
                self.adicionar_log(f"Consumidor <- recebeu: {msg}")
                self.atualizar_interface()
                time.sleep(random.uniform(1, 2))
            except Empty:
                self.adicionar_log("Consumidor esperando mensagem...")
                time.sleep(0.5)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
