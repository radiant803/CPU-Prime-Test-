import math
import multiprocessing as mp
import time


def simple_sieve(limit):
    """Basic sieve to generate small primes up to sqrt(n)"""
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]

    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False

    return [i for i, is_prime in enumerate(sieve) if is_prime]


def segmented_sieve(start, end, small_primes):
    """Segmented sieve for a range"""
    segment_size = end - start
    sieve = [True] * segment_size

    for p in small_primes:
        first_multiple = max(p * p, ((start + p - 1) // p) * p)
        for j in range(first_multiple, end, p):
            sieve[j - start] = False

    primes = []
    for i in range(segment_size):
        if sieve[i] and (start + i) > 1:
            primes.append(start + i)

    return primes


def worker(start, segment_size, small_primes):
    """Worker process to compute primes in a segment"""
    end = start + segment_size
    primes = segmented_sieve(start, end, small_primes)
    return len(primes)  # returning count keeps memory low


def main():
    print("Starting high-speed CPU prime search...")
    
    cpu_count = mp.cpu_count()
    print(f"Using {cpu_count} CPU cores")

    segment_size = 1_000_000  # adjust for performance
    max_limit = 10**12        # effectively "infinite" loop

    small_primes = simple_sieve(int(math.sqrt(max_limit)))

    pool = mp.Pool(cpu_count)

    start = 2
    total_primes = 0

    t0 = time.time()

    try:
        while True:
            tasks = []
            for i in range(cpu_count):
                seg_start = start + i * segment_size
                tasks.append((seg_start, segment_size, small_primes))

            results = pool.starmap(worker, tasks)

            total_primes += sum(results)
            start += cpu_count * segment_size

            elapsed = time.time() - t0

            print(f"Checked up to {start:,} | Total primes found: {total_primes:,} | Time: {elapsed:.2f}s")

    except KeyboardInterrupt:
        print("\nStopped by user.")
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
