import threading
import time
import random
from collections import deque
import tkinter as tk

class SolucaoJustaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Leitores e Escritores - Solução Justa")

        self.NUM_LEITORES = 3
        self.NUM_ESCRITORES = 2
        self.TOTAL_MENSAGENS = 10

        self.buffer = deque(maxlen=self.TOTAL_MENSAGENS)
        self.readcount = 0
        self.mensagens_restantes = self.TOTAL_MENSAGENS

        self.fila = threading.Semaphore(1)
        self.rw_mutex = threading.Semaphore(1)
        self.mutex = threading.Semaphore(1)
        self.buffer_lock = threading.Lock()
        self.mensagens_lock = threading.Lock()

        self.highlighted_indices = set()
        self.highlight_lock = threading.Lock()

        self.running = True
        self.setup_ui()

        self.leitores = []
        self.escritores = []

    def setup_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_top, text="Leitores:").grid(row=0, column=0, sticky="w")
        self.entry_leitores = tk.Entry(frame_top, width=5)
        self.entry_leitores.insert(0, str(self.NUM_LEITORES))
        self.entry_leitores.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(frame_top, text="Escritores:").grid(row=0, column=2, sticky="w")
        self.entry_escritores = tk.Entry(frame_top, width=5)
        self.entry_escritores.insert(0, str(self.NUM_ESCRITORES))
        self.entry_escritores.grid(row=0, column=3, sticky="w", padx=5)

        tk.Label(frame_top, text="Total mensagens:").grid(row=0, column=4, sticky="w")
        self.entry_total = tk.Entry(frame_top, width=5)
        self.entry_total.insert(0, str(self.TOTAL_MENSAGENS))
        self.entry_total.grid(row=0, column=5, sticky="w", padx=5)

        self.btn_start = tk.Button(frame_top, text="Iniciar", command=self.start_simulation)
        self.btn_start.grid(row=0, column=6, padx=10)

        tk.Label(self.root, text="Buffer:").pack(anchor="w", padx=10)
        self.buffer_frame = tk.Frame(self.root, relief="sunken", borderwidth=1, height=50)
        self.buffer_frame.pack(padx=10, pady=5, fill="x")

        tk.Label(self.root, text="Logs:").pack(anchor="w", padx=10)
        self.text_logs = tk.Text(self.root, height=15, state="disabled")
        self.text_logs.pack(padx=10, pady=5, fill="both", expand=True)

    def log(self, message):
        def inner():
            self.text_logs.config(state="normal")
            self.text_logs.insert("end", message + "\n")
            # Scroll automático desativado
            self.text_logs.config(state="disabled")
        self.root.after(0, inner)

    def update_buffer_display(self):
        def inner():
            for widget in self.buffer_frame.winfo_children():
                widget.destroy()

            if not self.buffer:
                return

            with self.highlight_lock:
                highlights = self.highlighted_indices.copy()

            for i, msg in enumerate(self.buffer):
                lbl = tk.Label(self.buffer_frame, text=msg, relief="raised", padx=5, pady=2)
                lbl.pack(side="left", padx=2)
                if i in highlights:
                    lbl.config(bg="#ccffcc")
        self.root.after(0, inner)

    def leitor(self, id_leitor):
        while self.running:
            with self.mensagens_lock:
                if self.mensagens_restantes <= 0 and len(self.buffer) == 0:
                    break

            self.fila.acquire()

            self.mutex.acquire()
            if self.readcount == 0:
                self.rw_mutex.acquire()
            self.readcount += 1
            self.mutex.release()

            # Leitura
            with self.buffer_lock:
                if len(self.buffer) > 0:
                    idx = random.randint(0, len(self.buffer) - 1)
                    item = self.buffer[idx]
                else:
                    idx = None
                    item = None

            if item is not None:
                with self.highlight_lock:
                    self.highlighted_indices.add(idx)
                self.update_buffer_display()
                self.log(f"📖 [LEITOR {id_leitor}] leu: {item}")
                time.sleep(random.uniform(0.5, 1.2))
                with self.highlight_lock:
                    self.highlighted_indices.discard(idx)
                self.update_buffer_display()

            self.mutex.acquire()
            self.readcount -= 1
            if self.readcount == 0:
                self.rw_mutex.release()
            self.mutex.release()

            self.fila.release()

            time.sleep(random.uniform(0.3, 0.7))

    def escritor(self, id_escritor, qtd_mensagens):
        for _ in range(qtd_mensagens):
            if not self.running:
                break

            time.sleep(random.uniform(1.0, 2.0))  # Delay para destacar alternância

            self.fila.acquire()
            self.rw_mutex.acquire()
            self.fila.release()

            with self.mensagens_lock:
                if self.mensagens_restantes <= 0:
                    self.rw_mutex.release()
                    return

                self.mensagens_restantes -= 1
                msg = f"msg-{self.TOTAL_MENSAGENS - self.mensagens_restantes}"

            with self.buffer_lock:
                self.buffer.append(msg)
            self.log(f"✍️ [ESCRITOR {id_escritor}] escreveu: {msg}")
            self.update_buffer_display()

            self.rw_mutex.release()

        if id_escritor == self.NUM_ESCRITORES:
            self.log("\n" + "✨" * 10 + " TODOS OS ESCRITORES TERMINARAM " + "✨" * 10 + "\n")

    def start_simulation(self):
        try:
            self.NUM_LEITORES = int(self.entry_leitores.get())
            self.NUM_ESCRITORES = int(self.entry_escritores.get())
            self.TOTAL_MENSAGENS = int(self.entry_total.get())
        except Exception:
            self.log("❌ Por favor, insira números válidos!")
            return

        self.buffer = deque(maxlen=self.TOTAL_MENSAGENS)
        self.mensagens_restantes = self.TOTAL_MENSAGENS
        self.readcount = 0
        self.highlighted_indices = set()
        self.running = True

        self.fila = threading.Semaphore(1)
        self.rw_mutex = threading.Semaphore(1)
        self.mutex = threading.Semaphore(1)

        self.text_logs.config(state="normal")
        self.text_logs.delete("1.0", "end")
        self.text_logs.config(state="disabled")
        self.update_buffer_display()

        self.leitores.clear()
        self.escritores.clear()

        base = self.TOTAL_MENSAGENS // self.NUM_ESCRITORES
        resto = self.TOTAL_MENSAGENS % self.NUM_ESCRITORES

        for i in range(self.NUM_ESCRITORES):
            qtd = base + (1 if i < resto else 0)
            t = threading.Thread(target=self.escritor, args=(i + 1, qtd), daemon=True)
            self.escritores.append(t)
            t.start()

        for i in range(self.NUM_LEITORES):
            t = threading.Thread(target=self.leitor, args=(i + 1,), daemon=True)
            self.leitores.append(t)
            t.start()

    def stop(self):
        self.running = False

def main():
    root = tk.Tk()
    app = SolucaoJustaApp(root)

    def on_closing():
        app.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
