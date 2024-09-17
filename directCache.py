import sys

class IO:
    def output(self, s):
        print(s, end='')

    def input(self, prompt):
        return input(prompt)

class EnderecoInvalido(Exception):
    def __init__(self, ender):
        self.ender = ender

class Memoria:
    def __init__(self, tam):
        self.tamanho = tam

    def capacidade(self):
        return self.tamanho

    def verifica_endereco(self, ender):
        if (ender < 0) or (ender >= self.tamanho):
            raise EnderecoInvalido(ender)

class RAM(Memoria):
    def __init__(self, k):
        Memoria.__init__(self, 2**k)
        self.memoria = [0] * self.tamanho

    def read(self, ender):
        self.verifica_endereco(ender)
        return self.memoria[ender]

    def write(self, ender, val):
        self.verifica_endereco(ender)
        self.memoria[ender] = val

class CPU:
    def __init__(self, mem, io):
        self.mem = mem
        self.io = io
        self.PC = 0
        self.A = self.B = self.C = 0

    def run(self, ender):
        self.PC = ender
        self.A = self.mem.read(self.PC)
        self.PC += 1
        self.B = self.mem.read(self.PC)
        self.PC += 1
        self.C = 1
        while self.A <= self.B:
            self.mem.write(self.A, self.C)
            self.io.output(f"{self.A} -> {self.C}\n")
            self.C += 1
            self.A += 1

class Cache(Memoria):
    def __init__(self, total_cache_lines, cache_line_size, ram):
        self.cache_lines = 2 ** total_cache_lines
        self.cache_line_size = 2 ** cache_line_size
        self.ram = ram
        self.dados = [0] * self.cache_line_size
        self.bloco_atual = -1
        self.tag_atual = -1
        self.modif = False

    def extrai_bits(self, endereco):
        return (
            endereco & (self.cache_line_size - 1),
            (endereco >> self.cache_line_size) & (self.cache_lines - 1),
            endereco >> (self.cache_line_size + self.cache_lines)
        )
        
    def InCache(self, ender, w, r, t):
        if self.cache_hit(r, t):
            print(f"Cache HIT: {ender}")
            return True
        else:
            print(f"Cache MISS: {ender}")
            bloco_ender = r * self.cache_line_size
            if self.modif:
                for i in range(self.cache_line_size):
                    self.ram.write(bloco_ender + i, self.dados[i])
            for i in range(self.cache_line_size):
                self.dados[i] = self.ram.read(bloco_ender + i)
            self.bloco = r
            self.tag = t
            self.modif = False
            return False

    def read(self, ender):
        w, r, t = self.extrai_bits(ender)
        self.InCache(ender, w, r, t)
        return self.dados[w]

    def write(self, ender, val):
        w, r, t = self.extrai_bits(ender)
        if not self.InCache(ender, w, r, t):
            pass
        self.dados[w] = val
        self.modif = True

    def cache_hit(self, r, t):
        return r == self.bloco_atual and t == self.tag_atual

try:
    io = IO()
    ram = RAM(12)
    cache = Cache(7, 4, ram)
    cpu = CPU(cache, io)
    inicio = 0
    ram.write(inicio, 110)
    ram.write(inicio + 1, 130)
    cpu.run(inicio)

except EnderecoInvalido as e:
    print("Endereco inválido:", e.ender, file=sys.stderr)
