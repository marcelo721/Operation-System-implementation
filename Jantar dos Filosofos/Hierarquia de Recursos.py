import threading
import time

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
    def __init__(self, name, left_fork, right_fork):
        threading.Thread.__init__(self)
        self.name = name
        # Garfos organizados por ordem de ID para evitar deadlock
        self.first_fork, self.second_fork = (left_fork, right_fork) if left_fork.id < right_fork.id else (right_fork, left_fork)

    def run(self):
        for _ in range(3):  # Comer 3 vezes para a simulação
            self.think()
            self.eat()

    def think(self):
        print(f"{self.name} está pensando.")
        time.sleep(1)

    def eat(self):
        print(f"{self.name} está tentando pegar {self.first_fork}")
        self.first_fork.acquire()
        print(f"{self.name} pegou {self.first_fork}")

        print(f"{self.name} está tentando pegar {self.second_fork}")
        self.second_fork.acquire()
        print(f"{self.name} pegou {self.second_fork}")

        print(f"{self.name} está COMENDO 🍝")
        time.sleep(2)

        self.first_fork.release()
        self.second_fork.release()
        print(f"{self.name} largou os garfos e voltou a pensar.\n")

def main():
    # Criar garfos (recursos)
    forks = [Fork(i) for i in range(5)]

    # Criar filósofos e associar garfos (esquerda e direita)
    philosophers = []
    names = ["Sócrates", "Platão", "Aristóteles", "Descartes", "Confúcio"]

    for i in range(5):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % 5]
        philosopher = Philosopher(names[i], left_fork, right_fork)
        philosophers.append(philosopher)

    # Iniciar a simulação
    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()
