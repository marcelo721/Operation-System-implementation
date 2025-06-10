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

class Arbiter:
    def __init__(self, max_allowed):
        self.max_allowed = max_allowed
        self.current = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

    def request_permission(self):
        with self.condition:
            while self.current >= self.max_allowed:
                self.condition.wait()
            self.current += 1

    def release_permission(self):
        with self.condition:
            self.current -= 1
            self.condition.notify_all()

class Philosopher(threading.Thread):
    def __init__(self, name, left_fork, right_fork, arbiter, max_meals=3):
        threading.Thread.__init__(self)
        self.name = name
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.arbiter = arbiter
        self.meals_eaten = 0
        self.max_meals = max_meals

    def run(self):
        while self.meals_eaten < self.max_meals:
            self.think()
            self.eat()

    def think(self):
        print(f"{self.name} está pensando.")
        time.sleep(1)

    def eat(self):
        print(f"{self.name} pede permissão ao árbitro para comer.")
        self.arbiter.request_permission()
        print(f"{self.name} recebeu permissão do árbitro.")

        # Pega os garfos
        self.left_fork.acquire()
        self.right_fork.acquire()

        print(f"{self.name} está COMENDO 🍝 ({self.meals_eaten + 1}/{self.max_meals})")
        time.sleep(2)
        self.meals_eaten += 1

        # Solta os garfos
        self.left_fork.release()
        self.right_fork.release()

        print(f"{self.name} largou os garfos e avisa o árbitro.")
        self.arbiter.release_permission()

def main():
    forks = [Fork(i) for i in range(5)]
    arbiter = Arbiter(max_allowed=4)  # máximo 4 filósofos simultaneamente
    names = ["Sócrates", "Platão", "Aristóteles", "Descartes", "Confúcio"]

    philosophers = []
    for i in range(5):
        left_fork = forks[i]
        right_fork = forks[(i + 1) % 5]
        philosopher = Philosopher(names[i], left_fork, right_fork, arbiter)
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()

    for p in philosophers:
        p.join()

if __name__ == "__main__":
    main()
