#Felipe Kureski
#Henrique Grigoli
#Théo Nicoleli

import sys

class IO:
    def output(self, s):
        print(s, end='')

class EnderecoInvalido(Exception):
    def __init__(self, ender):
        self.ender = ender

class RAM:
    def __init__(self, k):
        self.tamanho = 2**k
        self.dados_memoria = [0] * self.tamanho

    def verifica_endereco(self, ender):
        if ender < 0 or ender >= self.tamanho:
            raise EnderecoInvalido(ender)

    def read(self, ender):
        self.verifica_endereco(ender)
        return self.dados_memoria[ender]

    def write(self, ender, valor):
        self.verifica_endereco(ender)
        self.dados_memoria[ender] = valor

class CPU:
    def __init__(self, mem, io):
        self.mem = mem
        self.io = io
        self.PC, self.A, self.B, self.C = 0, 0, 0, 0

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

class Cache:
    def __init__(self, linhas_cache, tamanho_linha_cache, ram):
        self.linhas_cache = 2**linhas_cache
        self.tamanho_linha_cache = 2**tamanho_linha_cache
        self.k_linha_cache = tamanho_linha_cache  
        self.k_indice = linhas_cache 
        self.ram = ram
        self.linha_dados = [0] * self.tamanho_linha_cache
        self.linha_atual = -1
        self.modificada = False

    def extrai_bits(self, ender):
        print(f"Endereço em binário: {bin(ender)}")
        w = ender & ((1 << self.k_linha_cache) - 1)
        r = (ender >> self.k_linha_cache) & ((1 << self.k_indice) - 1)
        t = ender >> (self.k_linha_cache + self.k_indice)
        
        print('Valor de W =', bin(w))
        print('Valor de R =', bin(r))
        print('Valor de T =', bin(t))

        return w, r, t

    def read(self, ender):
        self.verifica_cache(ender)
        w, r, t = self.extrai_bits(ender)
        self.in_cache(ender, w, r, t)
        return self.linha_dados[w]

    def write(self, ender, valor):
        self.verifica_cache(ender)
        w, r, t = self.extrai_bits(ender)
        if not self.in_cache(ender, w, r, t):
            pass
        self.linha_dados[w] = valor
        self.modificada = True

    def in_cache(self, ender, w, r, t):
        if r == self.linha_atual:  
            print(f"Cache HIT no endereço: {ender}")
            return True
        else:
            print(f"Cache MISS no endereço: {ender}")
            self.atualizar_bloco(r)  
            return False

    def atualizar_bloco(self, r):
        if self.modificada:
            endereco_bloco = self.linha_atual * self.tamanho_linha_cache
            for i in range(self.tamanho_linha_cache):
                self.ram.write(endereco_bloco + i, self.linha_dados[i])

        endereco_bloco = r * self.tamanho_linha_cache
        for i in range(self.tamanho_linha_cache):
            self.linha_dados[i] = self.ram.read(endereco_bloco + i)

        self.linha_atual = r
        self.modificada = False

    def verifica_cache(self, ender):
        if ender >= self.ram.tamanho:  
            raise EnderecoInvalido(ender)

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
    print("Endereço inválido:", e.ender, file=sys.stderr)
