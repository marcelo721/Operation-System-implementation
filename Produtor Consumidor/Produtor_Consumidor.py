import random
import threading
import multiprocessing
import time
import tkinter as tk
from queue import Queue

class ProdConsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Produtor-Consumidor")
        self.root.geometry("900x600")

        self.text = tk.Text(self.root, font=("Consolas", 11), bg="#1e1e1e", fg="#dcdcdc")
        self.text.pack(expand=True, fill=tk.BOTH)

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.start_button = tk.Button(
            control_frame,
            text="Iniciar Produção e Consumo",
            command=self.start_threads,
            bg="#f44336",
            fg="white"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

       

        self.max_items = 20 
        self.buffer_size = 5  
        self.work_queue = Queue(maxsize=self.buffer_size)  
        self.production_finished = False
        self.running = False

    def display(self, msg, color=None):
        threadname = threading.current_thread().name
        processname = multiprocessing.current_process().name
        full_msg = f'🧵 [{threadname}] 🔄 [{processname}] 👉 {msg}\n'
        
        self.text.tag_config("error", foreground="#ff6666")
        self.text.tag_config("warning", foreground="#ffcc66")
        self.text.tag_config("success", foreground="#66ff66")
        self.text.tag_config("problem", foreground="#ff66ff")
        
        self.text.insert(tk.END, full_msg)
        
        if color == "error":
            self.text.tag_add("error", "end-2l linestart", "end-1l lineend")
        elif color == "warning":
            self.text.tag_add("warning", "end-2l linestart", "end-1l lineend")
        elif color == "success":
            self.text.tag_add("success", "end-2l linestart", "end-1l lineend")
        elif color == "problem":
            self.text.tag_add("problem", "end-2l linestart", "end-1l lineend")
            
        self.text.see(tk.END)

    
    #Funções principais de produtor e consumidor 
    def create_work(self):
        self.display("🚧 Iniciando produção PROBLEMÁTICA (sem verificações)", "warning")
        
        for x in range(self.max_items):
            if not self.running:
                break
                
            v = random.randint(1, 100)
            
            try:
                self.work_queue.put(v, block=False)  
                self.display(f'📦 Produzido item {x+1}/{self.max_items}: valor = {v}')
            except:
                self.display(f'💥 ERRO GRAVE: Tentou inserir em buffer CHEIO! (item {x+1})', "error")
               
            
            time.sleep(random.uniform(0.1, 0.3)) 

        self.production_finished = True
        self.display('⛔ Produção finalizada (de forma problemática)', "warning")

    def consume_work(self):
        counter = 0
        while self.running and (not self.production_finished or not self.work_queue.empty()):
            try:
                v = self.work_queue.get(block=False) 
                counter += 1
                self.display(f'📥 Consumido item {counter}: valor = {v}')
            except:
                self.display('💥 ERRO GRAVE: Tentou consumir de buffer VAZIO!', "error")
                
            
            time.sleep(random.uniform(0.2, 0.5))  

        self.display('⛔ Consumo finalizado (de forma problemática)', "warning")
    ###############################################################################
    
    
    def start_threads(self):
        if self.running:
            return
            
        self.running = True
        self.production_finished = False
        self.text.delete(1.0, tk.END)  
        
        self.display('⚠️ INICIANDO DEMONSTRAÇÃO DOS PROBLEMAS ⚠️', "error")
        self.display('Produtor vai tentar inserir mesmo com buffer cheio', "warning")
        self.display('Consumidor vai tentar consumir mesmo com buffer vazio', "warning")
        self.display('Isso simula o que acontece SEM os algoritmos de sincronização', "error")
        
        while not self.work_queue.empty():
            self.work_queue.get()
            
        producer = threading.Thread(target=self.create_work, name="Produtor-Problemático", daemon=True)
        consumer = threading.Thread(target=self.consume_work, name="Consumidor-Problemático", daemon=True)

        producer.start()
        consumer.start()

        def monitor():
            producer.join()
            consumer.join()
            self.running = False
            self.display('\n✅ Demonstração concluída (com erros intencionais)', "success")
            self.display('Estes são os problemas que os algoritmos de sincronização resolvem', "problem")
            
        threading.Thread(target=monitor, daemon=True).start()

if __name__ == '__main__':
    root = tk.Tk()
    app = ProdConsGUI(root)
    root.mainloop()