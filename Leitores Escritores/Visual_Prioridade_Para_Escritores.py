import threading
import time
import random
from collections import deque
import tkinter as tk
from tkinter import ttk

class SimuladorLE:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitores e Escritores - Prioridade para Escritores")

        self.setup_interface()
        self.running = False

    def setup_interface(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.grid()

        ttk.Label(frame, text="Leitores:").grid(column=0, row=0, sticky="w")
        self.leitores_input = ttk.Entry(frame, width=5)
        self.leitores_input.insert(0, "5")
        self.leitores_input.grid(column=1, row=0)

        ttk.Label(frame, text="Escritores:").grid(column=0, row=1, sticky="w")
        self.escritores_input = ttk.Entry(frame, width=5)
        self.escritores_input.insert(0, "2")
        self.escritores_input.grid(column=1, row=1)

        ttk.Label(frame, text="Mensagens:").grid(column=0, row=2, sticky="w")
        self.mensagens_input = ttk.Entry(frame, width=5)
        self.mensagens_input.insert(0, "50")
        self.mensagens_input.grid(column=1, row=2)

        ttk.Label(frame, text="Tamanho do Buffer:").grid(column=0, row=3, sticky="w")
        self.buffer_input = ttk.Entry(frame, width=5)
        self.buffer_input.insert(0, "10")
        self.buffer_input.grid(column=1, row=3)

        self.iniciar_btn = ttk.Button(frame, text="Iniciar Simulação", command=self.iniciar_simulacao)
        self.iniciar_btn.grid(column=0, row=4, columnspan=2, pady=10)

        ttk.Label(frame, text="Buffer:").grid(column=2, row=0, padx=10, sticky="w")
        self.buffer_cells = []
        self.buffer_frame = ttk.Frame(frame, borderwidth=2, relief="sunken")
        self.buffer_frame.grid(column=2, row=1, rowspan=4, padx=10, sticky="nsew")

        # Criar labels fixos para representar buffer vazio/cheio
        for i in range(20):  # máximo 20 espaços para layout, será ajustado depois
            label = tk.Label(self.buffer_frame, text="(vazio)", width=15, relief="ridge", bg="lightgray")
            label.grid(row=i, column=0, sticky="ew", pady=1)
            self.buffer_cells.append(label)

        self.log_display = tk.Text(frame, width=70, height=15, state="disabled")
        self.log_display.grid(column=0, row=5, columnspan=3, pady=10)

    def iniciar_simulacao(self):
        if self.running:
            return  # Evitar múltiplos clicks

        self.running = True
        self.iniciar_btn.config(state="disabled")

        # Ler inputs
        self.NUM_LEITORES = int(self.leitores_input.get())
        self.NUM_ESCRITORES = int(self.escritores_input.get())
        self.TOTAL_MENSAGENS = int(self.mensagens_input.get())
        self.TAMANHO_BUFFER = int(self.buffer_input.get())

        # Resetar buffer visual
        for i, cell in enumerate(self.buffer_cells):
            if i < self.TAMANHO_BUFFER:
                cell.config(text="(vazio)", bg="lightgray")
                cell.grid()
            else:
                cell.grid_remove()

        # Variáveis e semáforos
        self.buffer = deque(maxlen=self.TAMANHO_BUFFER)
        self.readcount = 0
        self.write_request = 0
        self.mensagens_restantes = self.TOTAL_MENSAGENS

        self.mutex = threading.Semaphore(1)
        self.write = threading.Semaphore(1)
        self.empty = threading.Semaphore(self.TAMANHO_BUFFER)
        self.full = threading.Semaphore(0)
        self.mensagens_lock = threading.Lock()

        self.threads = []
        msgs_por_escritor = self.TOTAL_MENSAGENS // self.NUM_ESCRITORES

        # Iniciar escritores
        for i in range(self.NUM_ESCRITORES):
            t = threading.Thread(target=self.escritor, args=(i + 1, msgs_por_escritor))
            t.daemon = True
            self.threads.append(t)
            t.start()

        # Iniciar leitores
        for i in range(self.NUM_LEITORES):
            t = threading.Thread(target=self.leitor, args=(i + 1,))
            t.daemon = True
            self.threads.append(t)
            t.start()

        # Thread para monitorar término dos escritores e finalizar
        threading.Thread(target=self.monitorar_finalizacao, daemon=True).start()

    def atualizar_buffer_visual(self):
        # Atualiza os labels do buffer para mostrar as mensagens e espaços vazios
        msgs = list(self.buffer)
        for i in range(self.TAMANHO_BUFFER):
            if i < len(msgs):
                self.buffer_cells[i].config(text=msgs[i], bg="lightgreen")
            else:
                self.buffer_cells[i].config(text="(vazio)", bg="lightgray")

    def log(self, texto, tipo="info"):
        self.log_display.config(state="normal")
        if tipo == "leitor":
            tag = "leitor"
        elif tipo == "escritor":
            tag = "escritor"
        else:
            tag = "info"
        self.log_display.insert(tk.END, texto + "\n", tag)
        self.log_display.see(tk.END)
        self.log_display.config(state="disabled")

        self.log_display.tag_config("leitor", foreground="blue")
        self.log_display.tag_config("escritor", foreground="green")
        self.log_display.tag_config("info", foreground="black")

    def leitor(self, id_leitor):
        while True:
            time.sleep(random.uniform(0.2, 1))
            self.full.acquire()

            while True:
                self.mutex.acquire()
                if self.write_request == 0:
                    self.readcount += 1
                    if self.readcount == 1:
                        self.write.acquire()
                    self.mutex.release()
                    break
                self.mutex.release()
                time.sleep(0.05)

            # Seção crítica de leitura
            if self.buffer:
                item = self.buffer.popleft()
                self.root.after(0, self.atualizar_buffer_visual)
                self.root.after(0, lambda i=id_leitor, itm=item: self.log(f"[LEITOR {i}] leu: {itm}", "leitor"))

            time.sleep(random.uniform(0.2, 0.5))

            self.mutex.acquire()
            self.readcount -= 1
            if self.readcount == 0:
                self.write.release()
            self.mutex.release()

            self.empty.release()

    def escritor(self, id_escritor, qtd_mensagens):
        for _ in range(qtd_mensagens):
            time.sleep(random.uniform(0.5, 1.5))

            with self.mensagens_lock:
                if self.mensagens_restantes <= 0:
                    return
                self.mensagens_restantes -= 1
                nova_mensagem = f"msg-{self.TOTAL_MENSAGENS - self.mensagens_restantes} (E{id_escritor})"

            self.empty.acquire()

            self.mutex.acquire()
            self.write_request += 1
            self.mutex.release()

            self.write.acquire()

            self.buffer.append(nova_mensagem)
            self.root.after(0, self.atualizar_buffer_visual)
            self.root.after(0, lambda i=id_escritor, msg=nova_mensagem: self.log(f">>> [ESCRITOR {i}] escreveu: {msg}", "escritor"))

            time.sleep(random.uniform(0.5, 1))

            self.write.release()

            self.mutex.acquire()
            self.write_request -= 1
            self.mutex.release()

            self.full.release()

    def monitorar_finalizacao(self):
        # Espera todos escritores terminarem
        for t in self.threads:
            if t.is_alive():
                t.join()

        # Depois espera um tempinho para leitores lerem buffer restante
        time.sleep(3)

        self.root.after(0, lambda: self.log("\n[INFO] Todos os escritores terminaram.", "info"))
        self.root.after(0, lambda: self.log("[INFO] Aguardando leitores processarem o restante do buffer...", "info"))

        # Espera mais um pouco
        time.sleep(5)

        self.root.after(0, lambda: self.log("\n[FIM] Simulação encerrada.", "info"))
        self.root.after(0, lambda: self.iniciar_btn.config(state="normal"))
        self.running = False


if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorLE(root)
    root.mainloop()
