import time
import random
import multiprocessing
import threading

iterations = 2 * 512 * 512

'''
# - Obiectul de tip Pool definit in modulul multiprocessing ofera o varianta buna de paralelizare a executiei unei
# functii cu mai multe valori de intrare, distribuind datele catre mai multe procese (data parallelism)
# - In acest sens, se defineste obiectul de tip Pool si se specifica numarul de procese in care sa se distribuie
# executia functiei
# - Se foloseste functia map care primeste ca parametru functia ce se doreste a fi executata si vectorul de valori de
# intrare care se va itera pentru distribuirea datelor catre mai multe procese
# - De asemenea, functia porneste executia acestor procese si asteapta terminarea tuturor proceselor, returnand rezultatul
# fiecarui proces si compunandu-le intr-o lista
'''


# functie care calculeaza timpul necesar executarii functiei Sequence (data prin pointer la functie)
def Time_Measurement(sequence, message):
    start_time = time.time_ns()
    sequence()
    stop_time = time.time_ns()
    exec_time = (stop_time - start_time) / 1e9
    print(f"Timpul de executie {message} : {exec_time} secunde")

def OrdinaryLoop(iterations):
    x = [random.randint(1,10000)] * int(iterations)
    for i in range(int(iterations)):
        arr = []
        arr.append(random.randint(1, 100))
        arr.append(random.randint(1, 1000))
        arr.append(random.randint(1, 10))
        arr.append(random.randint(1, 10000))
        arr.append(random.randint(1, 1000))
        arr.append(random.randint(1, 1000))
        arr.append(random.randint(1, 10))
        arr.append(random.randint(1, 10))

        x[i] *= pow(arr[0] + arr[1] / arr[2] - arr[3] * arr[4] / arr[5], arr[6]) * arr[7]
    return x

def SingleThreadSequence():
    x = OrdinaryLoop(iterations)

def MultiThreadSequence5():
    processes = 5
    interval = [iterations / processes] * processes
    with multiprocessing.Pool(processes=processes) as pool:
       x = pool.map(func=OrdinaryLoop, iterable=interval)

def MultiThreadSequence10():
    processes = 10
    interval = [iterations / processes] * processes
    pool = multiprocessing.Pool(processes=processes)
    x = pool.map(func=OrdinaryLoop, iterable=interval)

def MultiThreadSequence20():
    processes = 20
    interval = [iterations / processes] * processes
    pool = multiprocessing.Pool(processes=processes)
    x = pool.map(func=OrdinaryLoop, iterable=interval)


if __name__ == "__main__":
    threading.Thread(target=Time_Measurement, args=(SingleThreadSequence, "Single Thread", )).start()
    Time_Measurement(MultiThreadSequence5, "Multi Thread 5")
    Time_Measurement(MultiThreadSequence10, "Multi Thread 10")
    Time_Measurement(MultiThreadSequence20, "Multi Thread 20")
