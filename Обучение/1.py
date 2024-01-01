import pandas as pd
from scipy.stats import iqr, pearsonr, fisher_exact
import os

# Функция для чтения CSV файлов
def read_csv(file_path):
    data = pd.read_csv(file_path)
    return data

# Функция для расчета общего балла
def calculate_overall_score(data, w1, w2):
    # Предположим, что у вас есть как минимум два столбца в данных
    score1 = data.iloc[:, :2]
    score2 = data.iloc[:, 2:]

    overall_score = w1 * (100 * (score1.iloc[:, 0] / 20) + (score1.iloc[:, 1] * (score1.iloc[:, 1] - score1.iloc[:, 0]) / 20)) + \
                    w2 * (100 * (score2.iloc[:, 0] / 20) + (score2.iloc[:, 1] * (score2.iloc[:, 1] - score2.iloc[:, 0]) / 20))

    return overall_score

# Функция для расчета статистических параметров
def calculate_statistical_parameters(data):
    # Расчет среднего значения
    mean = data.mean()
    # Расчет медианы
    median = data.median()
    # Расчет моды
    mode = data.mode().iloc[0]  # Мода может быть представлена серией, берем первое значение
    # Расчет стандартного отклонения
    std_dev = data.std()
    # Расчет доверительного интервала
    ci = data.sem() * 1.96
    # Расчет коэффициента вариации
    cv = (std_dev / mean) * 100
    # Расчет интерквартильного размаха
    iqr_data = iqr(data)
    # Расчет коэффициента корреляции Пирсона
    correlation = pearsonr(data.iloc[:, 0], data.iloc[:, 1])[0]
    # Расчет коэффициента Фишера
    fisher_correlation = fisher_exact(data.iloc[:, :2])[0]
    # Расчет коэффициента вариации относительно исходного значения
    cv_orig = (std_dev / data.iloc[0]) * 100
    return mean, median, mode, std_dev, ci, cv, iqr_data, correlation, fisher_correlation, cv_orig

# Функция для записи результатов в Excel
def write_to_excel(results, file_path):
    df = pd.DataFrame(results)
    df.to_excel(file_path, index=False)

# Список для хранения результатов
results = []

# Цикл по папкам и файлам
for dir_path, dir_names, file_names in os.walk('D:\\!!! Phyton projects\\Bll\\'):
    for file_name in file_names:
        if file_name.endswith('.csv'):
            # Чтение файла
            file_path = os.path.join(dir_path, file_name)
            data = read_csv(file_path)
            # Расчет общего балла
            overall_score = calculate_overall_score(data, 0.6, 0.4)
            # Расчет статистических параметров
            stats = calculate_statistical_parameters(data)
            # Добавление результатов в список
            results.append([file_name, overall_score, stats])

# Запись результатов в Excel
write_to_excel(results, 'results.xlsx')
