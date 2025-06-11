import threading
import time
import random
from collections import deque

# Configurações
NUM_LEITORES = 3
NUM_ESCRITORES = 2
TOTAL_MENSAGENS = 51

# Variáveis compartilhadas
buffer = deque(maxlen=TOTAL_MENSAGENS)
readcount = 0
mensagens_restantes = TOTAL_MENSAGENS

# Semáforos
fila = threading.Semaphore(1)          # Fila única (justiça)
rw_mutex = threading.Semaphore(1)      # Excluir acesso simultâneo de leitores e escritores
mutex = threading.Semaphore(1)         # Protege readcount
buffer_lock = threading.Lock()         # Protege acesso ao buffer
mensagens_lock = threading.Lock()      # Protege contador de mensagens
full = threading.Semaphore(0)          # Quantidade de mensagens disponíveis para leitura

def leitor(id_leitor):
    global readcount, mensagens_restantes

    while True:
        # Condição de parada
        with mensagens_lock:
            if mensagens_restantes <= 0 and full._value == 0:
                break

        full.acquire()  # Aguarda existir mensagem para leitura
        fila.acquire()
        mutex.acquire()
        readcount += 1
        if readcount == 1:
            rw_mutex.acquire()
        mutex.release()
        fila.release()

        # Leitura protegida
        with buffer_lock:
            if len(buffer) > 0:
                item = random.choice(list(buffer))
                print(f"📖 [LEITOR {id_leitor}] leu: {item}")
            else:
                print(f"❌ [LEITOR {id_leitor}] ERRO: tentou ler buffer vazio!")

        mutex.acquire()
        readcount -= 1
        if readcount == 0:
            rw_mutex.release()
        mutex.release()

        time.sleep(random.uniform(0.3, 0.7))

def escritor(id_escritor, qtd_mensagens):
    global mensagens_restantes

    for _ in range(qtd_mensagens):
        time.sleep(random.uniform(0.3, 0.7))

        fila.acquire()
        rw_mutex.acquire()

        with mensagens_lock:
            if mensagens_restantes <= 0:
                rw_mutex.release()
                fila.release()
                return

            mensagens_restantes -= 1
            msg = f"msg-{TOTAL_MENSAGENS - mensagens_restantes}"

        with buffer_lock:
            buffer.append(msg)
            print(f"✍️ [ESCRITOR {id_escritor}] escreveu: {msg}")

        full.release()  # Sinaliza que há nova mensagem para leitores
        rw_mutex.release()
        fila.release()

def main():
    leitores = []
    escritores = []

    base = TOTAL_MENSAGENS // NUM_ESCRITORES
    resto = TOTAL_MENSAGENS % NUM_ESCRITORES

    for i in range(NUM_ESCRITORES):
        qtd = base + (1 if i < resto else 0)
        t = threading.Thread(target=escritor, args=(i + 1, qtd))
        escritores.append(t)
        t.start()

    for i in range(NUM_LEITORES):
        t = threading.Thread(target=leitor, args=(i + 1,))
        leitores.append(t)
        t.start()

    for t in escritores:
        t.join()

    print("\n" + "✨" * 10 + " TODOS OS ESCRITORES TERMINARAM " + "✨" * 10 + "\n")

    for t in leitores:
        t.join()

    print("✅ Leitura concluída. Programa encerrado com sucesso.")

if __name__ == "__main__":
    main()
