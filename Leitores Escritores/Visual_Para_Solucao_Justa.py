import threading
import time
import random
from tkinter import *
from tkinter import ttk
from collections import deque


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Problema dos Leitores e Escritores - Acesso Justo")

        # Entrada de parâmetros
        self.setup_controls()

        # Área visual do buffer
        self.buffer_display = []
        self.setup_buffer_area()

        # Log
        self.log_area = Text(root, height=10, width=80, state=DISABLED)
        self.log_area.pack(pady=10)

    def setup_controls(self):
        frame = Frame(self.root)
        frame.pack(pady=10)

        Label(frame, text="Leitores:").grid(row=0, column=0)
        self.num_leitores = Spinbox(frame, from_=1, to=20, width=5)
        self.num_leitores.grid(row=0, column=1)

        Label(frame, text="Escritores:").grid(row=0, column=2)
        self.num_escritores = Spinbox(frame, from_=1, to=20, width=5)
        self.num_escritores.grid(row=0, column=3)

        Label(frame, text="Mensagens Totais:").grid(row=0, column=4)
        self.total_mensagens = Spinbox(frame, from_=1, to=100, width=5)
        self.total_mensagens.grid(row=0, column=5)

        Label(frame, text="Tamanho do Buffer:").grid(row=0, column=6)
        self.tamanho_buffer = Spinbox(frame, from_=1, to=20, width=5)
        self.tamanho_buffer.grid(row=0, column=7)

        self.btn_iniciar = Button(frame, text="Iniciar Simulação", command=self.iniciar_simulacao)
        self.btn_iniciar.grid(row=0, column=8, padx=10)

    def setup_buffer_area(self):
        self.buffer_frame = Frame(self.root)
        self.buffer_frame.pack(pady=10)

    def atualizar_buffer_visual(self, buffer):
        for widget in self.buffer_frame.winfo_children():
            widget.destroy()

        self.buffer_display.clear()
        for i in range(self.buffer_maxlen):
            text = buffer[i] if i < len(buffer) else "vazio"
            label = Label(self.buffer_frame, text=text, width=12, height=2, relief=RIDGE, bg="#e0e0e0")
            label.grid(row=0, column=i, padx=2)
            self.buffer_display.append(label)

    def adicionar_log(self, msg):
        self.log_area.config(state=NORMAL)
        self.log_area.insert(END, msg + "\n")
        self.log_area.see(END)
        self.log_area.config(state=DISABLED)

    def iniciar_simulacao(self):
        self.btn_iniciar.config(state=DISABLED)

        leitores = int(self.num_leitores.get())
        escritores = int(self.num_escritores.get())
        total_msgs = int(self.total_mensagens.get())
        tam_buffer = int(self.tamanho_buffer.get())

        self.buffer_maxlen = tam_buffer
        self.app_thread = threading.Thread(target=self.executar_simulacao,
                                           args=(leitores, escritores, total_msgs, tam_buffer), daemon=True)
        self.app_thread.start()

    def executar_simulacao(self, num_leitores, num_escritores, total_mensagens, tam_buffer):
        buffer = deque(maxlen=tam_buffer)
        mutex = threading.Semaphore(1)
        write = threading.Semaphore(1)
        empty = threading.Semaphore(tam_buffer)
        full = threading.Semaphore(0)
        fila = threading.Semaphore(1)

        readcount = [0]
        mensagens_restantes = [total_mensagens]
        mensagens_lock = threading.Lock()

        # Funções internas
        def leitor(id_leitor):
            while True:
                time.sleep(random.uniform(0.2, 1))
                full.acquire()
                fila.acquire()
                mutex.acquire()
                readcount[0] += 1
                if readcount[0] == 1:
                    write.acquire()
                mutex.release()
                fila.release()

                # leitura
                item = buffer.popleft()
                self.root.after(0, self.adicionar_log, f"[LEITOR {id_leitor}] leu: {item}")
                self.root.after(0, self.atualizar_buffer_visual, list(buffer))
                time.sleep(random.uniform(0.2, 0.5))

                mutex.acquire()
                readcount[0] -= 1
                if readcount[0] == 0:
                    write.release()
                mutex.release()

                empty.release()

        def escritor(id_escritor, qtd_mensagens):
            for _ in range(qtd_mensagens):
                time.sleep(random.uniform(0.5, 1.5))
                with mensagens_lock:
                    if mensagens_restantes[0] <= 0:
                        return
                    mensagens_restantes[0] -= 1
                    nova_mensagem = f"msg-{total_mensagens - mensagens_restantes[0]} (E{id_escritor})"

                empty.acquire()
                fila.acquire()
                write.acquire()
                fila.release()

                buffer.append(nova_mensagem)
                self.root.after(0, self.adicionar_log, f">>> [ESCRITOR {id_escritor}] escreveu: {nova_mensagem}")
                self.root.after(0, self.atualizar_buffer_visual, list(buffer))
                time.sleep(random.uniform(0.5, 1))

                write.release()
                full.release()

        # Distribuição justa das mensagens
        msgs_por_escritor = [total_mensagens // num_escritores] * num_escritores
        for i in range(total_mensagens % num_escritores):
            msgs_por_escritor[i] += 1

        leitores_threads = []
        escritores_threads = []

        for i in range(num_escritores):
            t = threading.Thread(target=escritor, args=(i + 1, msgs_por_escritor[i]), daemon=True)
            escritores_threads.append(t)
            t.start()

        for i in range(num_leitores):
            t = threading.Thread(target=leitor, args=(i + 1,), daemon=True)
            leitores_threads.append(t)
            t.start()

        for t in escritores_threads:
            t.join()

        self.root.after(0, self.adicionar_log, "\n[INFO] Todos os escritores terminaram. Aguardando leitores...\n")
        time.sleep(3)
        self.root.after(0, self.adicionar_log, "\n[FIM] Simulação encerrada.")
        self.btn_iniciar.config(state=NORMAL)


if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
