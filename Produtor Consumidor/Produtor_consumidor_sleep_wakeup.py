import tkinter as tk
import threading
import time
import random
import math

class ProdutorConsumidorGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Produtor-Consumidor com Sleep/WakeUp")
        self.buffer_size = 10
        self.buffer = []
        self.producer_sleeping = False
        self.consumer_sleeping = False
        self.wake_up_lost = False

        self.lock = threading.Lock()

        # Layout principal
        self.setup_ui()

        # Threads
        threading.Thread(target=self.producer, daemon=True).start()
        threading.Thread(target=self.consumer, daemon=True).start()
        

    def setup_ui(self):
        self.master.configure(bg="#f0f0f0")

        # Frame do buffer
        buffer_frame = tk.LabelFrame(self.master, text="Buffer", padx=10, pady=10, bg="#f0f0f0")
        buffer_frame.pack(pady=10)

        self.buffer_labels = []
        for i in range(self.buffer_size):
            lbl = tk.Label(buffer_frame, text="Vazio", width=10, height=2, bg="#d3d3d3", relief=tk.RAISED, font=("Arial", 10, "bold"))
            lbl.pack(side=tk.LEFT, padx=5)
            self.buffer_labels.append(lbl)

        # Status dos agentes
        self.status_label = tk.Label(self.master, text="Status inicial", font=("Arial", 11), bg="#f0f0f0")
        self.status_label.pack(pady=5)

        # Log
        log_frame = tk.LabelFrame(self.master, text="Logs", padx=10, pady=5, bg="#f0f0f0")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.log_text = tk.Text(log_frame, height=10, bg="black", fg="lime", font=("Courier", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def update_ui(self):
        for i in range(self.buffer_size):
            if i < len(self.buffer):
                self.buffer_labels[i]["text"] = self.buffer[i]
                self.buffer_labels[i]["bg"] = "#a3ffa3"  # verde claro
            else:
                self.buffer_labels[i]["text"] = "Vazio"
                self.buffer_labels[i]["bg"] = "#d3d3d3"  # cinza

        state = f"Produtor: {'😴 Dormindo' if self.producer_sleeping else '🟢 Ativo'} | "
        state += f"Consumidor: {'😴 Dormindo' if self.consumer_sleeping else '🟢 Ativo'}"
        self.status_label.config(text=state)


##funções principais de sleep e wakeup
    def sleep(self, role):
        if role == "producer":
            self.producer_sleeping = True
            self.log("[Produtor] Dormindo (buffer cheio)")
        else:
            self.consumer_sleeping = True
            self.log("[Consumidor] Dormindo (buffer vazio)")
        self.update_ui()

    def wake_up(self, role):
        if role == "producer":
            if self.producer_sleeping:
                self.producer_sleeping = False
                self.log("[Produtor] Acordado")
        else:
            if self.consumer_sleeping:
                self.consumer_sleeping = False
                self.log("[Consumidor] Acordado")
        self.update_ui()

    def producer(self):
        while True:
            item = f"Item{random.randint(1, 99)}"
            #with self.lock:
            if len(self.buffer) >= self.buffer_size:
                self.sleep("producer")
            else:
                if self.producer_sleeping:
                    self.wake_up("producer")
                self.buffer.append(item)
                self.log(f"[Produtor] Produziu: {item}")
                self.update_ui()
                if self.consumer_sleeping:
                    self.wake_up("consumer")
            time.sleep(random.uniform(0.5,1.5))
        
    def consumer(self):
        while True:
            #with self.lock:
            if len(self.buffer) == 0:
                self.sleep("consumer")
            else:
                if self.consumer_sleeping:
                    self.wake_up("consumer")
                consumed = self.buffer.pop(0)
                self.log(f"[Consumidor] Consumiu: {consumed}")
                self.update_ui()
                if self.producer_sleeping:
                    self.wake_up("producer")
            time.sleep(random.uniform(0.5, 1.5))

###################################################################################

if __name__ == "__main__":
    root = tk.Tk()
    app = ProdutorConsumidorGUI(root)
    root.geometry("1024x700")
    root.mainloop()
