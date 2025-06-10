import random
import threading
import time
import tkinter as tk

# ===============================
# Classe da Interface Gráfica
# ===============================
class ProdConsGUI:
    def __init__(self, root):
        self.total_produced = 0
        self.root = root
        self.root.title("Produtor-Consumidor com Semáforos")
        self.root.geometry("900x700")

        # Entradas para configuração
        self.config_frame = tk.Frame(self.root)
        self.config_frame.pack(pady=10)

        tk.Label(self.config_frame, text="🧱 Tamanho do Buffer:", font=("Consolas", 11)).grid(row=0, column=0, padx=5)
        self.buffer_entry = tk.Entry(self.config_frame, width=5)
        self.buffer_entry.insert(0, "10")  # valor padrão
        self.buffer_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.config_frame, text="🎯 Itens a produzir:", font=("Consolas", 11)).grid(row=0, column=2, padx=5)
        self.items_entry = tk.Entry(self.config_frame, width=5)
        self.items_entry.insert(0, "50")  # valor padrão
        self.items_entry.grid(row=0, column=3, padx=5)


        # Text area para log
        self.text = tk.Text(self.root, font=("Consolas", 11), bg="#1e1e1e", fg="#dcdcdc", height=15)
        self.text.pack(expand=False, fill=tk.X)

        # Labels dos semáforos
        self.semaforo_frame = tk.Frame(self.root)
        self.semaforo_frame.pack(pady=5)

        self.mutex_label = tk.Label(self.semaforo_frame, text="🛡️ Mutex: 1", font=("Consolas", 12), width=20)
        self.mutex_label.grid(row=0, column=0)

        self.empty_label = tk.Label(self.semaforo_frame, text="⬜ Empty: 10", font=("Consolas", 12), width=20)
        self.empty_label.grid(row=0, column=1)

        self.full_label = tk.Label(self.semaforo_frame, text="🟦 Full: 0", font=("Consolas", 12), width=20)
        self.full_label.grid(row=0, column=2)

        # Visualização do buffer
        self.buffer_frame = tk.Frame(self.root)
        self.buffer_frame.pack(pady=10)

        self.buffer_labels = []
        for i in range(10):  # buffer de tamanho 10
            lbl = tk.Label(self.buffer_frame, text="🕳️", font=("Consolas", 16), width=4, borderwidth=2, relief="groove")
            lbl.grid(row=0, column=i, padx=2)
            self.buffer_labels.append(lbl)

        # Botão iniciar
        self.start_button = tk.Button(
            self.root, text="Iniciar Produção e Consumo",
            command=self.start_threads, bg="#4CAF50", fg="white", font=("Consolas", 12)
        )
        self.start_button.pack(pady=10)

        # Configurações
        self.buffer_size = 10
        self.buffer = []

        self.max_items = 50

        self.mutex = threading.Semaphore(1)
        self.empty = threading.Semaphore(self.buffer_size)
        self.full = threading.Semaphore(0)

        self.production_done = False

    def display(self, msg):
        threadname = threading.current_thread().name
        full_msg = f'🧵 [{threadname}] 👉 {msg}\n'
        self.text.insert(tk.END, full_msg)
        self.text.see(tk.END)
        self.update_semaphores()
        self.update_buffer()

    def update_semaphores(self):
        self.mutex_label.config(text=f"🛡️ Mutex: {self.mutex._value}")
        self.empty_label.config(text=f"⬜ Empty: {self.empty._value}")
        self.full_label.config(text=f"🟦 Full: {self.full._value}")

    def update_buffer(self):
        for i in range(self.buffer_size):
            if i < len(self.buffer):
                self.buffer_labels[i].config(text=str(self.buffer[i]))
            else:
                self.buffer_labels[i].config(text="🕳️")

    # principais métodos de produção e consumo
    # produtor e consumidor com semáforos
    def producer(self):
        for i in range(self.max_items):
            item = random.randint(1, 100)

            self.empty.acquire()
            self.mutex.acquire()

            self.buffer.append(item)
            self.display(f'📦 Produzido item {i+1}/{self.max_items}: valor = {item}')
            self.total_produced += 1

            self.mutex.release()
            self.full.release()
            time.sleep(0.2 + len(self.buffer) * 0.05)


        self.production_done = True
        self.display('✅ Produção finalizada.')

    def consumer(self):
        counter = 0
        while True:
            if self.production_done and self.full._value == 0:
                break

            self.full.acquire()
            self.mutex.acquire() 

            if self.buffer:
                item = self.buffer.pop(0)
                counter += 1
                self.display(f'📥 Consumido item {counter}: valor = {item}')
            else:
                self.display('⚠️ Buffer vazio por engano!')

            self.mutex.release()
            self.empty.release()
            time.sleep(0.2 + (self.buffer_size - len(self.buffer)) * 0.05)



        self.display('🏁 Todos os itens consumidos.')
    #############################################################################
    
    
    def start_threads(self):
        try:
            self.buffer_size = int(self.buffer_entry.get())
            self.max_items = int(self.items_entry.get())
        except ValueError:
            self.display("❌ Erro: valores inválidos. Use números inteiros.")
            return

        if self.buffer_size <= 0 or self.max_items <= 0:
            self.display("❌ Erro: valores devem ser positivos.")
            return

        self.reset_simulation()
        self.display('🚀 Iniciando produção e consumo com semáforos...')
        producer_thread = threading.Thread(target=self.producer, daemon=True, name="Produtor")
        consumer_thread = threading.Thread(target=self.consumer, daemon=True, name="Consumidor")

        producer_thread.start()
        consumer_thread.start()

    def reset_simulation(self):
        self.buffer.clear()
        self.text.delete("1.0", tk.END)
        self.production_done = False

        self.mutex = threading.Semaphore(1)
        self.empty = threading.Semaphore(self.buffer_size)
        self.full = threading.Semaphore(0)

        # Recria visualização do buffer
        for widget in self.buffer_frame.winfo_children():
            widget.destroy()
        self.buffer_labels = []
        for i in range(self.buffer_size):
            lbl = tk.Label(self.buffer_frame, text="🕳️", font=("Consolas", 16), width=4, borderwidth=2, relief="groove")
            lbl.grid(row=0, column=i, padx=2)
            self.buffer_labels.append(lbl)

        self.update_semaphores()
        self.update_buffer()
# ===============================
# Execução da GUI
# ===============================
if __name__ == '__main__':
    root = tk.Tk()
    app = ProdConsGUI(root)
    root.mainloop()
