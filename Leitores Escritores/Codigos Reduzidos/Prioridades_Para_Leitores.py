import threading
import time
import random
from collections import deque

# Configurações
TOTAL_MENSAGENS = 10
TAMANHO_BUFFER = TOTAL_MENSAGENS
NUM_LEITORES = 3
NUM_ESCRITORES = 2

# Buffer e controles
buffer = deque(maxlen=TAMANHO_BUFFER)
mutex = threading.Semaphore(1)       # Protege readcount
write = threading.Semaphore(1)       # Exclusividade para escritores
empty = threading.Semaphore(TAMANHO_BUFFER)  # Espaços vazios
full = threading.Semaphore(0)        # Itens disponíveis para leitura
mutex_b = threading.Semaphore(1)     # Protege o buffer (se necessário)

readcount = 0
mensagens_restantes = TOTAL_MENSAGENS
mensagens_lock = threading.Lock()    # Protege mensagens_restantes

def leitor(id_leitor):
    global readcount

    while True:
        time.sleep(random.uniform(0.5, 1.5))  # Delay para acompanhar logs

        # Protocolo de entrada (prioridade para leitores)
        mutex.acquire()
        readcount += 1
        if readcount == 1:
            write.acquire()  # Bloqueia escritores no primeiro leitor
        mutex.release()

        # Leitura aleatória (segura, pois escritores estão bloqueados)
        if len(buffer) > 0:
            idx = random.randint(0, len(buffer) - 1)
            item = buffer[idx]
            print(f"📖 [LEITOR {id_leitor}] leu: '{item}' (posição {idx})")
        else:
            print(f"🛑 [LEITOR {id_leitor}] buffer vazio")

        # Protocolo de saída
        mutex.acquire()
        readcount -= 1
        if readcount == 0:
            write.release()  # Libera escritores se não houver leitores
        mutex.release()

        time.sleep(1)  # Delay adicional para logs legíveis

def escritor(id_escritor, qtd_mensagens):
    global mensagens_restantes

    for _ in range(qtd_mensagens):
        time.sleep(random.uniform(0.5, 1.5))  # Delay entre escritas

        # Verifica se ainda há mensagens para escrever
        mensagens_lock.acquire()
        if mensagens_restantes <= 0:
            mensagens_lock.release()
            return
        mensagens_restantes -= 1
        nova_mensagem = f"msg-{TOTAL_MENSAGENS - mensagens_restantes}"
        mensagens_lock.release()

        # Protocolo de escrita
        empty.acquire()  # Espera espaço no buffer
        write.acquire()  # Exclusividade para escrita

        mutex_b.acquire()
        buffer.append(nova_mensagem)
        mutex_b.release()
        print(f"✍️ [ESCRITOR {id_escritor}] escreveu: '{nova_mensagem}'")

        write.release()
        full.release()  # Sinaliza que há novos itens

def main():
    leitores = []
    escritores = []

    # Distribui mensagens igualmente entre escritores
    base = TOTAL_MENSAGENS // NUM_ESCRITORES
    resto = TOTAL_MENSAGENS % NUM_ESCRITORES

    # Inicia escritores
    for i in range(NUM_ESCRITORES):
        qtd = base + (1 if i < resto else 0)
        t = threading.Thread(target=escritor, args=(i + 1, qtd))
        escritores.append(t)
        t.start()

    # Inicia leitores (rodam para sempre)
    for i in range(NUM_LEITORES):
        t = threading.Thread(target=leitor, args=(i + 1,))
        leitores.append(t)
        t.start()

    # Espera escritores terminarem
    for t in escritores:
        t.join()

    print("\n✅ Todos os escritores terminaram. Leitores continuam lendo eternamente...\n")

    # Manter o programa rodando (interrompa com Ctrl+C)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🚀 Programa encerrado manualmente.")

if __name__ == "__main__":
    main()