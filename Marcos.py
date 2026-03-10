import hashlib
import time
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

# --- CONFIGURAÇÕES ---
TARGET_HASH = "ca6ae33116b93e57b87810a27296fc36"
# Ajustado para garantir que a soma dos testes (1 a 12 threads) fique sob 400s
MAX_SEARCH = 450000000 
WORKERS_TO_TEST = [1, 2, 4, 8, 12]

def check_range(start, end):
    """Função executada por cada processo (Worker)"""
    for i in range(start, end):
        # Formata com 9 dígitos (ex: 000000001)
        candidate = f"{i:09d}".encode()
        if hashlib.md5(candidate).hexdigest() == TARGET_HASH:
            return i
    return None

def run_test(num_workers):
    """Gerencia a divisão do trabalho e mede o tempo"""
    chunk_size = MAX_SEARCH // num_workers
    ranges = [(i * chunk_size, (i + 1) * chunk_size) for i in range(num_workers)]
    ranges[-1] = (ranges[-1][0], MAX_SEARCH) # Garante que cubra até o fim

    start_time = time.time()
    found_password = None
    
    # Uso de ProcessPoolExecutor para contornar o GIL do Python
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(check_range, r[0], r[1]) for r in ranges]
        for future in futures:
            result = future.result()
            if result is not None:
                found_password = result
    
    end_time = time.time()
    return end_time - start_time, found_password

if __name__ == "__main__":
    tempos = []
    
    print(f"{'Threads':<10} | {'Tempo (s)':<12} | {'Senha Encontrada':<15}")
    print("-" * 45)

    for w in WORKERS_TO_TEST:
        duracao, psw = run_test(w)
        tempos.append(duracao)
        print(f"{w:<10} | {duracao:<12.2f} | {psw}")

    # --- CÁLCULOS DE PERFORMANCE ---
    t1 = tempos[0]
    # Speedup (S) = T1 / Tn
    speedups = [t1 / tn for tn in tempos]
    # Eficiência (E) = S / n
    eficiencia = [s / n for s, n in zip(speedups, WORKERS_TO_TEST)]

    # --- GERAÇÃO DOS GRÁFICOS ---
    plt.figure(figsize=(12, 5))
    
    # Gráfico de Speedup
    plt.subplot(1, 2, 1)
    plt.plot(WORKERS_TO_TEST, speedups, marker='o', color='b', label='Realizado')
    plt.plot(WORKERS_TO_TEST, WORKERS_TO_TEST, '--', color='gray', label='Ideal')
    plt.title("Gráfico de Speedup ($S$)")
    plt.xlabel("Número de Processos (Threads)")
    plt.ylabel("Speedup")
    plt.legend()
    plt.grid(True)

    # Gráfico de Eficiência
    plt.subplot(1, 2, 2)
    plt.plot(WORKERS_TO_TEST, eficiencia, marker='s', color='r')
    plt.title("Gráfico de Eficiência ($E$)")
    plt.xlabel("Número de Processos (Threads)")
    plt.ylabel("Eficiência (0 a 1)")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("resultado_paralelismo.png")
    print("\n[OK] Gráfico salvo como 'resultado_paralelismo.png'")
    plt.show()