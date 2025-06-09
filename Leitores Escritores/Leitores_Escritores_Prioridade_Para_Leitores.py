import threading
import time
import random
from collections import deque

# Configurações principais
TAMANHO_BUFFER = 5
TOTAL_MENSAGENS = 10
NUM_LEITORES = 5
NUM_ESCRITORES = 2

# Buffer e variáveis de controle
buffer = deque(maxlen=TAMANHO_BUFFER)
mutex = threading.Semaphore(1)               # Protege readcount
write = threading.Semaphore(1)               # Garante exclusividade de escrita
empty = threading.Semaphore(TAMANHO_BUFFER)  # Espaços vazios no buffer
full = threading.Semaphore(0)                # Itens disponíveis para leitura

readcount = 0                                # quantidade de leitores ativos
readcount_lock = threading.Lock()            # Protege readcount no Python
mensagens_restantes = TOTAL_MENSAGENS
mensagens_lock = threading.Lock()            # Protege mensagens_restantes


def leitor(id_leitor):
    global readcount

    while True:
        time.sleep(random.uniform(0.2, 1))  # tempo aleatório antes de tentar ler

        full.acquire()                      #espera ter arquivos no buffer para poder ler

        # Começa protocolo para acessar buffer com prioridade de leitores
        mutex.acquire()                     #garante que so um leitor altere o valor do readcount por vez
        readcount += 1
        if readcount == 1:
            write.acquire()                 # Primeiro leitor bloqueia escrita
        mutex.release() 
        #termina o processo de atualização do readcount e libera para o proximo leitor realizar a ação

        # Seção crítica de leitura
        item = buffer.popleft()
        if item is None:
            # Sinal de parada: reinserimos para outros leitores e saímos
            buffer.appendleft(None)
            full.release()
            empty.acquire()
            mutex.acquire()
            readcount -= 1
            if readcount == 0:
                write.release()
            mutex.release()
            break
        #processo para o leitor entender que nada mais sera adcionado no buffer e esperar infnitamente novos dados (simulação da morte do processo leitor)

        print(f"<<<[LEITOR {id_leitor}] leu: {item}")
        time.sleep(random.uniform(0.2, 0.5))

        # Finaliza leitura
        mutex.acquire()
        readcount -= 1
        if readcount == 0:
            write.release()                   # Último leitor libera escrita
        mutex.release()

        empty.release()  # Sinaliza que há um espaço livre no buffer


def escritor(id_escritor, qtd_mensagens):
    global mensagens_restantes

    for _ in range(qtd_mensagens):
        time.sleep(random.uniform(0.5, 1.5))

        # Garante que ainda temos mensagens para escrever
        with mensagens_lock:              #forma curta de escrever mensagens_lock.aqcure() /* codigo codigo codigo*/ mensagens_lock.release()
            if mensagens_restantes <= 0:
                return
            mensagens_restantes -= 1
            nova_mensagem = f"msg-{TOTAL_MENSAGENS - mensagens_restantes}"

        empty.acquire()                  #verifica se existe espaço livre no buffer para poder excrever
        write.acquire()                  #verifica se está liberado escrever (se nao houver nenhum outro escritor/leitor atuando)

        buffer.append(nova_mensagem)     #adcionando mensagem no buffer propriamente dito
        print(f">>> [ESCRITOR {id_escritor}] escreveu: {nova_mensagem}")
        time.sleep(random.uniform(0.5, 1))

        write.release()                  #libera a função de escrita para outro escritor que esteja esperando
        full.release()                   #sinaliza para os leitores que ha um novo item disponivel para leitura no buffer


def main():
    leitores = []
    escritores = []

    # Distribuição justa mesmo se TOTAL_MENSAGENS não for divisível pela quantidade de escritores
    base = TOTAL_MENSAGENS // NUM_ESCRITORES
    resto = TOTAL_MENSAGENS % NUM_ESCRITORES

    #criação das threads escritoras
    for i in range(NUM_ESCRITORES):
        qtd = base + (1 if i < resto else 0)
        t = threading.Thread(target=escritor, args=(i + 1, qtd))
        escritores.append(t)
        t.start()

    #criação das threads leitoras
    for i in range(NUM_LEITORES):
        t = threading.Thread(target=leitor, args=(i + 1,))
        leitores.append(t)
        t.start()

    for t in escritores:
        t.join()

    print("\n[INFO] Todos os escritores terminaram.")
    print("[INFO] Sinalizando leitores para encerramento...\n")

    # Sinaliza o fim para os leitores com mensagens especiais (None)
    for _ in range(NUM_LEITORES):
        empty.acquire()
        write.acquire()
        buffer.append(None)
        write.release()
        full.release()

    #para evitar que os leitores fiquem esperando infinitamente, pois se o buffer permanecer vazio por um tempo muito grande, é pq nao tera mais nada adcionado ali
    for t in leitores:
        t.join(timeout=3)


    print("\n[FIM] Simulação encerrada.")


if __name__ == "__main__":
    main()
