import subprocess
import concurrent.futures
import os

# Параметры
script_path = "scripts/authorize_users_from_csv.py"
data_file = "D:/Bll_tests/secrets/bulk_users.csv"
options = "--headless --relogin"
n_threads = 10

# Функция для запуска скрипта
def run_script(idx):
    command = f"python {script_path} {data_file} {options}"
    result = subprocess.run(command, shell=True)
    print(f"Поток {idx} завершен с кодом {result.returncode}")
    return result.returncode

# Запуск потоков
if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        futures = {executor.submit(run_script, i): i for i in range(n_threads)}

        for future in concurrent.futures.as_completed(futures):
            idx = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Поток {idx} завершился с ошибкой: {e}")

