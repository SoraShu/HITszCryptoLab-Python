#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python 3.9 or higher is needed for typing
import random
import secrets
import math
from functools import reduce, partial
from itertools import tee
from typing import Iterable

Keypair = tuple[int, int]

test_time = 8


def _miiller_test(d, n):
    a = 2 + random.randint(1, n - 4)
    x = pow(a, d, n)

    if (x == 1 or x == n - 1):
        return True

    while (d != n - 1):
        x = (x * x) % n
        d *= 2

        if (x == 1):
            return False
        if (x == n - 1):
            return True

    return False


def is_prime(n, k):

    if (n <= 1 or n == 4):
        return False
    if (n <= 3):
        return True

    d = n - 1
    while (d % 2 == 0):
        d //= 2

    for _ in range(k):
        if (_miiller_test(d, n) == False):
            return False

    return True


def gen_large_prime() -> int:
    # return sympy.nextprime(secrets.randbits(1024))
    large = secrets.randbits(2048)
    if large % 2 == 0:
        large += 1
    while not is_prime(large, test_time):
        large += 2
    return large


def read_hexstring(path: str) -> bytes:
    with open(path, 'rb') as f:
        return f.read()


def write_ints(path: str, data: Iterable[int]):
    with open(path, 'w+') as f:
        for i in data:
            f.write(str(i)+'\n')


def spilt_into_4bytes(data: bytes) -> Iterable[int]:
    buffer = []
    for b in data:
        buffer.append(b)
        if len(buffer) == 4:
            yield reduce(lambda x, y: x*256+y, buffer)
            buffer.clear()
    if len(buffer) != 0:
        while(len(buffer) != 4):
            buffer.append(0)
        yield reduce(lambda x, y: x*256+y, buffer)


def despilt_into_4bytes(data: Iterable[int]) -> bytes:
    res = []
    for num in data:
        buffer = []
        for i in range(4):
            buffer.append(num % 256)
            num = num // 256
        buffer.reverse()
        res.extend(buffer)

    return bytes(res)


def exgcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    d, x, y = exgcd(b, a % b)
    return d, y, x - (a // b) * y


def quick_pow(a: int, b: int, m: int) -> int:
    a = a % m
    res = 1
    while b > 0:
        if (b & 1):
            res = res * a % m
        a = a * a % m
        b >>= 1
    return res


def key_gen() -> tuple[Keypair, Keypair]:
    print('keygen start. ')
    p = gen_large_prime()
    q = gen_large_prime()

    n = p * q
    phi_n = (p-1) * (q-1)

    e = secrets.randbits(512)
    while(math.gcd(e, phi_n) != 1):
        e += 1

    _, d, _ = exgcd(e, phi_n)

    d = d if d > 0 else d + phi_n

    print(f'p = {p}\n')
    print(f'q = {q}\n')
    print(f'n = {n}\n')
    print(f'e = {e}\n')
    print(f'd = {d}\n')
    print(f'phi_n = {phi_n}\n')
    print('keygen end. \n')
    return (e, n), (d, n)


def _cry(text: int, key: Keypair) -> int:
    a, n = key
    return pow(text, a, n)


encrypt = _cry
decrypt = _cry


def main():
    raw = read_hexstring(r'./lab2-Plaintext.txt')
    print(f"text:\n{str(raw, 'ascii')}\n")
    text = spilt_into_4bytes(raw)
    pub, pri = key_gen()
    # print(pub)
    # print(pri)

    encrypted = map(partial(encrypt, key=pub), text)

    encrypted, to_write = tee(encrypted, 2)
    write_ints('./lab2_encripted', to_write)

    decrypted = map(partial(decrypt, key=pri), encrypted)

    decrypted_text = despilt_into_4bytes(decrypted)

    print(f"decrypted_text:\n{str(decrypted_text,'ascii')}\n")


if __name__ == '__main__':
    main()
