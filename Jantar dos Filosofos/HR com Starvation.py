import threading
import time
import random

class Fork:
    def __init__(self, id):
        self.id = id
        self.lock = threading.Lock()

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()

    def __repr__(self):
        return f"Garfo {self.id}"

class Philosopher(threading.Thread):
    def __init__(self, name, left_fork, right_fork, think_time):
        threading.Thread.__init__(self)
        self.name = name
        self.first_fork, self.second_fork = (left_fork, right_fork) if left_fork.id < right_fork.id else (right_fork, left_fork)
        self.think_time = think_time  # tempo variável para pensar, para simular starvation

    def run(self):
        for _ in range(5):
            self.think()
            self.eat()

    def think(self):
        print(f"{self.name} está pensando por {self.think_time:.2f} segundos.")
        time.sleep(self.think_time)

    def eat(self):
        print(f"{self.name} tenta pegar {self.first_fork}")
        self.first_fork.acquire()
        print(f"{self.name} pegou {self.first_fork}")

        print(f"{self.name} tenta pegar {self.second_fork}")
        self.second_fork.acquire()
        print(f"{self.name} pegou {self.second_fork}")

        print(f"{self.name} está COMENDO 🍝")
        time.sleep(2)

        self.first_fork.release()
        self.second_fork.release()
        print(f"{self.name} largou os garfos e voltou a pensar.\n")

def main():
    forks = [Fork(i) for i in range(5)]

    # Definimos tempos de pensar variáveis para simular starvation
    # Alguns filósofos pensam rápido (pegarão garfos mais rápido), outros lento
    think_times = [0.1, 0.1, 3, 0.1, 0.1]  # Sócrates pensará lento, pode passar fome

    names = ["Sócrates", "Platão", "Aristóteles", "Descartes", "Confúcio"]

    philosophers = []
    for i in range(5):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % 5]
        philosopher = Philosopher(names[i], left_fork, right_fork, think_times[i])
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()
