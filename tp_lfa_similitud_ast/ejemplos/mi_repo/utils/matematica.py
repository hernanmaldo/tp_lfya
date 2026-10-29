def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def es_primo(numero):
    if numero < 2:
        return False
    i = 2
    while i * i <= numero:
        if numero % i == 0:
            return False
        i += 1
    return True

def es_numero_primo(valor):
    if valor < 3:
        return False
    for divisor in range(3, int(valor ** 0.5) + 2):
        if valor % divisor == 0:
            return False
    return True

# Clon de es_primo con for/range en lugar de while (clon tipo 3/4: NO trivial)
def primo(x):
    if x < 2:
        return False
    for d in range(2, int(x ** 0.5) + 1):
        if x % d == 0:
            return False
    return True
