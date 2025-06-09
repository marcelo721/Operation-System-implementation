import threading
import time
import random
import tkinter as tk
from tkinter import ttk
from collections import deque

# ==============================
# Classe principal da interface
# ==============================
class Simulador:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulação: Leitores e Escritores")

        # === Parâmetros da Simulação ===
        self.total_mensagens = tk.IntVar(value=20)
        self.num_leitores = tk.IntVar(value=3)
        self.num_escritores = tk.IntVar(value=2)
        self.tamanho_buffer = tk.IntVar(value=10)

        # === Interface ===
        self._criar_interface()

        # === Estado da Simulação ===
        self.buffer = None
        self.buffer_lock = threading.Semaphore(1)
        self.write = threading.Semaphore(1)
        self.empty = None
        self.full = None
        self.readcount = 0
        self.readcount_lock = threading.Lock()
        self.mensagens_restantes = 0
        self.mensagens_lock = threading.Lock()

        self.leitores_threads = []
        self.escritores_threads = []

    def _criar_interface(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack()

        ttk.Label(frame, text="Total de mensagens:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.total_mensagens, width=5).grid(row=0, column=1)

        ttk.Label(frame, text="Leitores:").grid(row=1, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.num_leitores, width=5).grid(row=1, column=1)

        ttk.Label(frame, text="Escritores:").grid(row=2, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.num_escritores, width=5).grid(row=2, column=1)

        ttk.Label(frame, text="Tamanho do buffer:").grid(row=3, column=0, sticky="w")
        ttk.Entry(frame, textvariable=self.tamanho_buffer, width=5).grid(row=3, column=1)

        ttk.Button(frame, text="Iniciar Simulação", command=self.iniciar_simulacao).grid(row=4, column=0, columnspan=2, pady=10)

        # === Buffer visual ===
        self.buffer_frame = ttk.Frame(self.root, padding=10)
        self.buffer_frame.pack()

        self.buffer_labels = []

        # === Logs ===
        ttk.Label(self.root, text="Logs:").pack()
        self.log_text = tk.Text(self.root, height=15, width=80)
        self.log_text.pack()

    def atualizar_buffer_visual(self):
        for label in self.buffer_labels:
            label.destroy()
        self.buffer_labels = []

        for i in range(self.tamanho_buffer.get()):
            valor = self.buffer[i] if i < len(self.buffer) else ""
            bg = "lightgreen" if valor else "lightgray"
            txt = valor if valor else "vazio"
            label = ttk.Label(self.buffer_frame, text=txt, borderwidth=2, relief="groove", width=15)
            label.grid(row=0, column=i, padx=2, pady=5)
            self.buffer_labels.append(label)

    def log(self, mensagem):
        self.log_text.insert(tk.END, mensagem + "\n")
        self.log_text.see(tk.END)

    def iniciar_simulacao(self):
        # Reset estado
        self.log_text.delete("1.0", tk.END)
        self.buffer = deque(maxlen=self.tamanho_buffer.get())
        self.empty = threading.Semaphore(self.tamanho_buffer.get())
        self.full = threading.Semaphore(0)
        self.readcount = 0
        self.mensagens_restantes = self.total_mensagens.get()

        self.leitores_threads = []
        self.escritores_threads = []

        self.atualizar_buffer_visual()

        # Distribuição das mensagens
        total = self.total_mensagens.get()
        escritores = self.num_escritores.get()
        base = total // escritores
        resto = total % escritores

        for i in range(escritores):
            qtd = base + (1 if i < resto else 0)
            t = threading.Thread(target=self.escritor, args=(i + 1, qtd))
            self.escritores_threads.append(t)
            t.start()

        for i in range(self.num_leitores.get()):
            t = threading.Thread(target=self.leitor, args=(i + 1,))
            self.leitores_threads.append(t)
            t.start()

        threading.Thread(target=self.finalizar_depois).start()

    def finalizar_depois(self):
        for t in self.escritores_threads:
            t.join()

        self.log("[INFO] Todos os escritores terminaram. Enviando sinais de parada...")

        for _ in range(self.num_leitores.get()):
            self.empty.acquire()
            self.write.acquire()
            self.buffer.append(None)
            self.write.release()
            self.full.release()
            self.root.after(0, self.atualizar_buffer_visual)

        for t in self.leitores_threads:
            t.join(timeout=5)

        self.log("[FIM] Simulação encerrada.")

    def leitor(self, id_leitor):
        while True:
            time.sleep(random.uniform(0.2, 1))
            self.full.acquire()

            self.buffer_lock.acquire()
            self.readcount += 1
            if self.readcount == 1:
                self.write.acquire()
            self.buffer_lock.release()

            # Seção crítica de leitura
            item = self.buffer.popleft()
            self.root.after(0, self.atualizar_buffer_visual)

            if item is None:
                self.buffer.appendleft(None)
                self.full.release()
                self.empty.acquire()
                self.buffer_lock.acquire()
                self.readcount -= 1
                if self.readcount == 0:
                    self.write.release()
                self.buffer_lock.release()
                break

            self.log(f"[LEITOR {id_leitor}] leu: {item}")
            time.sleep(random.uniform(0.2, 0.5))

            self.buffer_lock.acquire()
            self.readcount -= 1
            if self.readcount == 0:
                self.write.release()
            self.buffer_lock.release()

            self.empty.release()

    def escritor(self, id_escritor, qtd_mensagens):
        for _ in range(qtd_mensagens):
            time.sleep(random.uniform(0.5, 1.5))
            with self.mensagens_lock:
                if self.mensagens_restantes <= 0:
                    return
                self.mensagens_restantes -= 1
                nova_mensagem = f"msg-{self.total_mensagens.get() - self.mensagens_restantes} (E{id_escritor})"

            self.empty.acquire()
            self.write.acquire()

            self.buffer.append(nova_mensagem)
            self.root.after(0, self.atualizar_buffer_visual)
            self.log(f">>> [ESCRITOR {id_escritor}] escreveu: {nova_mensagem}")
            time.sleep(random.uniform(0.5, 1))

            self.write.release()
            self.full.release()

# ==========================
# Execução
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    app = Simulador(root)
    root.mainloop()
