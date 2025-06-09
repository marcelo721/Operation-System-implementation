import threading
import time
import random
from collections import deque

# Configurações principais
TAMANHO_BUFFER = 10                           # Capacidade máxima do buffer
TOTAL_MENSAGENS = 20                          # Total de mensagens a serem produzidas
NUM_LEITORES = 5                              # Número de leitores simultâneos
NUM_ESCRITORES = 8                            # Número de escritores simultâneos

# Buffer e variáveis de controle
buffer = deque(maxlen=TAMANHO_BUFFER)         # Buffer circular com tamanho limitado
mutex = threading.Semaphore(1)                # Protege a variável readcount
write = threading.Semaphore(1)                # Exclusão mútua entre escritores e leitores
empty = threading.Semaphore(TAMANHO_BUFFER)   # Controla espaços disponíveis no buffer
full = threading.Semaphore(0)                 # Controla quantidade de itens disponíveis no buffer
fila = threading.Semaphore(1)                 # Garante acesso justo entre leitores e escritores

readcount = 0                                 # Número de leitores atualmente lendo
mensagens_restantes = TOTAL_MENSAGENS         # Quantidade de mensagens que ainda precisam ser escritas
mensagens_lock = threading.Lock()             # Protege acesso à variável mensagens_restantes


def leitor(id_leitor):
    global readcount

    while True:
        time.sleep(random.uniform(0.2, 1))   # Simula tempo entre tentativas de leitura

        full.acquire()                       # Espera até que haja pelo menos uma mensagem no buffer
        fila.acquire()                       # Aguarda sua vez na fila (garante ordem justa)
        mutex.acquire()                      # Protege a variável readcount
        readcount += 1
        if readcount == 1:
            write.acquire()                  # Primeiro leitor bloqueia escritores
        mutex.release()
        fila.release()                       # Libera a fila para o próximo leitor ou escritor

        # Seção crítica de leitura
        item = buffer.popleft()              # Remove mensagem do buffer
        print(f"[LEITOR {id_leitor}] leu: {item}")
        time.sleep(random.uniform(0.2, 0.5)) # Simula tempo de leitura

        mutex.acquire()
        readcount -= 1
        if readcount == 0:
            write.release()                  # Último leitor libera os escritores
        mutex.release()

        empty.release()                      # Sinaliza que há espaço no buffer


def escritor(id_escritor, qtd_mensagens):
    global mensagens_restantes

    for _ in range(qtd_mensagens):
        time.sleep(random.uniform(0.5, 1.5))   # Simula tempo de produção de mensagem

        with mensagens_lock:                   # Garante que escritores não ultrapassem TOTAL_MENSAGENS
            if mensagens_restantes <= 0:
                return
            mensagens_restantes -= 1
            nova_mensagem = f"msg-{TOTAL_MENSAGENS - mensagens_restantes} (E{id_escritor})"

        empty.acquire()                       # Espera até haver espaço no buffer
        fila.acquire()                        # Entra na fila de acesso justo
        write.acquire()                       # Acessa a região crítica de escrita
        fila.release()                        # Libera fila após entrar

        # Seção crítica de escrita
        buffer.append(nova_mensagem)          # Adiciona mensagem no buffer
        print(f">>> [ESCRITOR {id_escritor}] escreveu: {nova_mensagem}")
        time.sleep(random.uniform(0.5, 1))    # Simula tempo de escrita

        write.release()                       # Libera acesso para outros escritores/leitores
        full.release()                        # Sinaliza que há um novo item disponível no buffer


def main():
    leitores = []
    escritores = []

    # Distribui TOTAL_MENSAGENS entre os escritores de forma justa
    msgs_por_escritor = [TOTAL_MENSAGENS // NUM_ESCRITORES] * NUM_ESCRITORES
    resto = TOTAL_MENSAGENS % NUM_ESCRITORES
    for i in range(resto):
        msgs_por_escritor[i] += 1

    # Cria e inicia threads dos escritores
    for i in range(NUM_ESCRITORES):
        t = threading.Thread(target=escritor, args=(i + 1, msgs_por_escritor[i]))
        escritores.append(t)
        t.start()

    # Cria e inicia threads dos leitores
    for i in range(NUM_LEITORES):
        t = threading.Thread(target=leitor, args=(i + 1,))
        leitores.append(t)
        t.start()

    for t in escritores:
        t.join()                            # Aguarda finalização dos escritores

    print("\n[INFO] Todos os escritores terminaram.\nAguardando leitores processarem o restante do buffer...\n")

    for t in leitores:
        t.join(timeout=3)                   # Dá tempo para os leitores terminarem

    print("\n[FIM] Simulação encerrada.")


if __name__ == "__main__":
    main()
