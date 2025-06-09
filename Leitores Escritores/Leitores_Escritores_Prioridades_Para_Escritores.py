import threading
import time
import random
from collections import deque

# Configurações principais
TAMANHO_BUFFER = 10
TOTAL_MENSAGENS = 20
NUM_LEITORES = 5
NUM_ESCRITORES = 8

# Buffer e variáveis de controle
buffer = deque(maxlen=TAMANHO_BUFFER)
mutex = threading.Semaphore(1)               # Protege variáveis readcount e write_request
write = threading.Semaphore(1)               # Exclusão mútua para escritores
empty = threading.Semaphore(TAMANHO_BUFFER)  # Espaços livres no buffer
full = threading.Semaphore(0)                # Itens disponíveis no buffer

readcount = 0                                # Número de leitores atualmente lendo
write_request = 0                            # Quantidade de escritores esperando para escrever
mensagens_restantes = TOTAL_MENSAGENS
mensagens_lock = threading.Lock()            # Protege a variável mensagens_restantes


def leitor(id_leitor):
    global readcount, write_request

    while True:
        time.sleep(random.uniform(0.2, 1))  # Tempo aleatório antes de tentar ler

        full.acquire()                      # Aguarda até que haja pelo menos um item no buffer

        while True:
            mutex.acquire()                 # mutex para garantir que apenas 1 leitor faça essa verificação por vez
            if write_request == 0:
                # Se nenhum escritor estiver esperando, entra na leitura
                readcount += 1
                if readcount == 1:
                    write.acquire()        # Primeiro leitor bloqueia escritores
                mutex.release()            # libera para o proximo leitor executar caso nao tenha escritores em espera
                break
            mutex.release()                # libera para o proximo leitor, sem fazer nada, se tiver algum escritor esperando
            time.sleep(0.05)               # Espera um tempo antes de tentar novamente

        # Seção crítica de leitura
        item = buffer.popleft()            # Lê um item do buffer
        print(f"[LEITOR {id_leitor}] leu: {item}")
        time.sleep(random.uniform(0.2, 0.5))  # Simula tempo de leitura

        # Finaliza leitura
        mutex.acquire()                    # mutex para garantir que so um leitor faça a mudança por vez
        readcount -= 1
        if readcount == 0:
            write.release()                # Último leitor libera escritores
        mutex.release()

        empty.release()                    # Sinaliza que há espaço livre no buffer


def escritor(id_escritor, qtd_mensagens):
    global mensagens_restantes, write_request

    for _ in range(qtd_mensagens):
        time.sleep(random.uniform(0.5, 1.5))  # Simula tempo de produção da mensagem

        with mensagens_lock:                  # Protege acesso à quantidade de mensagens restantes
            if mensagens_restantes <= 0:
                return                        # Se não há mais mensagens para escrever, termina 
            mensagens_restantes -= 1
            nova_mensagem = f"msg-{TOTAL_MENSAGENS - mensagens_restantes} (E{id_escritor})"

        empty.acquire()                      # Verifica se há espaço no buffer

        mutex.acquire()                      # Garante que so um escritor faça a mudança por vez
        write_request += 1                   # Indica que há um escritor querendo escrever
        mutex.release()

        write.acquire()                      # Aguarda permissão para escrever

        # Seção crítica de escrita
        buffer.append(nova_mensagem)         # Escreve no buffer
        print(f">>> [ESCRITOR {id_escritor}] escreveu: {nova_mensagem}")
        time.sleep(random.uniform(0.5, 1))   # Simula tempo de escrita

        write.release()                      # Libera para outro escritor/leitor acessar

        mutex.acquire()
        write_request -= 1                   # Indica que terminou a escrita
        mutex.release()

        full.release()                       # Sinaliza que há um novo item disponível no buffer


def main():
    leitores = []
    escritores = []

    msgs_por_escritor = TOTAL_MENSAGENS // NUM_ESCRITORES  # Divide as mensagens entre os escritores

    # Criação das threads escritoras
    for i in range(NUM_ESCRITORES):
        t = threading.Thread(target=escritor, args=(i + 1, msgs_por_escritor))
        escritores.append(t)
        t.start()

    # Criação das threads leitoras
    for i in range(NUM_LEITORES):
        t = threading.Thread(target=leitor, args=(i + 1,))
        leitores.append(t)
        t.start()

    for t in escritores:
        t.join()                            # Espera todos os escritores terminarem

    print("\n[INFO] Todos os escritores terminaram.\nAguardando leitores processarem o restante do buffer...\n")
    
    for t in leitores:
        t.join(timeout=3)                   # Dá um tempo para os leitores terminarem

    print("\n[FIM] Simulação encerrada.")


if __name__ == "__main__":
    main()
