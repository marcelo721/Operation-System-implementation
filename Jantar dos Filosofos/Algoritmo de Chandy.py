class Fork:
    def __init__(self, id):
        self.id = id
        self.owner = None
        self.dirty = True  # todo garfo começa sujo

    def __repr__(self):
        return f"Garfo {self.id} (Dono: {self.owner.name}, {'Sujo' if self.dirty else 'Limpo'})"

class Philosopher:
    def __init__(self, name):
        self.name = name
        self.neighbors = []
        self.forks = {}  # garfos em posse: vizinho -> fork

    def add_neighbor(self, neighbor, fork):
        self.neighbors.append(neighbor)
        self.forks[neighbor] = fork

    def has_all_forks(self):
        return all(fork.owner == self for fork in self.forks.values())

    def request_forks(self):
        print(f"\n{self.name} quer comer.")
        for neighbor, fork in self.forks.items():
            if fork.owner != self:
                print(f"{self.name} pede o Garfo {fork.id} para {neighbor.name}")
                neighbor.give_fork(self)

    def give_fork(self, requester):
        fork = self.forks[requester]
        if fork.owner == self and fork.dirty:
            print(f"{self.name} entrega o Garfo {fork.id} para {requester.name}")
            fork.owner = requester
            fork.dirty = False
            del self.forks[requester]
            requester.forks[self] = fork

    def eat(self):
        if not self.has_all_forks():
            self.request_forks()
        if self.has_all_forks():
            print(f"{self.name} está COMENDO 🍝")
            for fork in self.forks.values():
                fork.dirty = True
        else:
            print(f"{self.name} não conseguiu todos os garfos e continua com fome.")

    def __repr__(self):
        return f"{self.name}"

# ----- Configuração inicial -----

# Criar filósofos
p1 = Philosopher("Filósofo 1")
p2 = Philosopher("Filósofo 2")
p3 = Philosopher("Filósofo 3")

# Criar garfos e distribuir dono inicial (p1 -> 0, p2 -> 1, p3 -> 2)
f0 = Fork(0); f0.owner = p1
f1 = Fork(1); f1.owner = p2
f2 = Fork(2); f2.owner = p3

# Conectar filósofos (modelo circular)
p1.add_neighbor(p2, f0)
p2.add_neighbor(p1, f0)

p2.add_neighbor(p3, f1)
p3.add_neighbor(p2, f1)

p3.add_neighbor(p1, f2)
p1.add_neighbor(p3, f2)

# ----- Simulação -----

p1.eat()
p2.eat()
p3.eat()
p1.eat()  # tentar novamente

print(f0.owner)
print(f1.owner)
print(f2.owner)