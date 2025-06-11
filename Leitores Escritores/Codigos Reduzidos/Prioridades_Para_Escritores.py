import threading
import time
import random
from collections import deque

# Configurações
NUM_LEITORES = 3
NUM_ESCRITORES = 2
TOTAL_MENSAGENS = 10

# Variáveis compartilhadas
buffer = deque(maxlen=TOTAL_MENSAGENS)
readcount = 0
writecount = 0
mensagens_restantes = TOTAL_MENSAGENS

# Semáforos
mutex = threading.Semaphore(1)         # Protege readcount
mutex2 = threading.Semaphore(1)        # Protege writecount
rw_mutex = threading.Semaphore(1)      # Exclusão entre leitores e escritores
tryread = threading.Semaphore(1)       # Impede novos leitores quando há escritor esperando
buffer_lock = threading.Lock()         # Protege buffer
mensagens_lock = threading.Lock()      # Protege contadores

def leitor(id_leitor):
    global readcount, mensagens_restantes

    while True:
        # Checagem se há algo a ser lido
        with mensagens_lock:
            if mensagens_restantes <= 0 and len(buffer) == 0:
                break

        # Leitores respeitam escritores esperando
        tryread.acquire()
        tryread.release()

        # Entrada do leitor
        mutex.acquire()
        readcount += 1
        if readcount == 1:
            rw_mutex.acquire()
        mutex.release()

        # Leitura
        with buffer_lock:
            if len(buffer) > 0:
                item = random.choice(list(buffer))
                print(f"📖 [LEITOR {id_leitor}] leu: {item}")
            else:
                print(f"📖 [LEITOR {id_leitor}] tentou ler, mas buffer estava vazio.")

        # Saída do leitor
        mutex.acquire()
        readcount -= 1
        if readcount == 0:
            rw_mutex.release()
        mutex.release()

        time.sleep(random.uniform(0.3, 0.7))

def escritor(id_escritor, qtd_mensagens):
    global writecount, mensagens_restantes

    for _ in range(qtd_mensagens):
        time.sleep(random.uniform(0.3, 0.7))

        # Entrada com prioridade
        mutex2.acquire()
        writecount += 1
        if writecount == 1:
            tryread.acquire()  # Primeiro escritor impede novos leitores
        mutex2.release()

        rw_mutex.acquire()

        # Escrita
        with mensagens_lock:
            if mensagens_restantes <= 0:
                rw_mutex.release()
                mutex2.acquire()
                writecount -= 1
                if writecount == 0:
                    tryread.release()
                mutex2.release()
                return

            mensagens_restantes -= 1
            msg = f"msg-{TOTAL_MENSAGENS - mensagens_restantes}"

        with buffer_lock:
            buffer.append(msg)
            print(f"✍️ [ESCRITOR {id_escritor}] escreveu: {msg}")

        rw_mutex.release()

        # Saída do escritor
        mutex2.acquire()
        writecount -= 1
        if writecount == 0:
            tryread.release()  # Último escritor libera leitores
        mutex2.release()

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
