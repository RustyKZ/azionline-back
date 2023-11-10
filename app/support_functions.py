# Преобразование строки в массив
def get_array(income_string):
    outcome_array=[]
    if income_string:
        # Разделяем строку по запятым и получаем список подстрок
        substrings = income_string.split(',')
        for substring in substrings:
            # Удаляем лишние пробелы вокруг подстроки
            cleaned_substring = substring.strip()
            if cleaned_substring:
                try:
                    # Преобразуем подстроку в целое число и добавляем в массив
                    num = int(cleaned_substring)
                    outcome_array.append(num)
                except ValueError:
                    # Если преобразование не удалось, игнорируем подстроку
                    pass
    return outcome_array

# И обратно
def set_array(income_array):
    outcome_string = ''
    if income_array:
        # Преобразуем каждый элемент массива в строку и объединяем их с помощью запятых
        outcome_string = ', '.join(str(num) for num in income_array)
    return outcome_string

def text_number(number):
    if not isinstance(number, (int, float)):
        return ''
    # Преобразовываем число в строку с разделением разрядов
    formatted_number = '{:,}'.format(number)
    formatted_number = formatted_number.replace(',', ' ')
    return formatted_number

def find_min_missing_natural(arr):
    if not arr:
        return 1  # Если массив пустой, возвращаем 1
    arr_set = set(arr)
    min_num = 1
    while min_num in arr_set:
        min_num += 1
    return min_num

def get_string_array(income_string):
    outcome_array = []
    substrings = income_string.split(',')
    for i in range(6):
        cleaned_substring = substrings[i].strip() if i < len(substrings) else ''
        outcome_array.append(cleaned_substring)
    return outcome_array

def set_string_array(income_array):
    outcome_string = ', '.join(income_array)
    return outcome_string

def get_bool_array(income_string):
    outcome_array = []
    if income_string:
        substrings = income_string.split(',')
        for substring in substrings:
            cleaned_substring = substring.strip()
            if cleaned_substring:
                outcome_array.append(cleaned_substring.lower() == 'true')
    return outcome_array

def set_bool_array(income_array):
    outcome_string = ', '.join(str(val).lower() for val in income_array)
    return outcome_string