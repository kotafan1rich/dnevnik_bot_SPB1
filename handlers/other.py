import pickle
import time
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from db import Database
import os.path
from dotenv import load_dotenv


load_dotenv()

db = Database('db_dnevnik_tg_bot.db')

bad_estimate_value_name = ['замечание', 'неизвестная', 'по болезни', 'зачёт']
bad_estimate_type_name = ['годовая', 'итоговая', 'четверть', 'посещаемость']
finals_estimate_type_name = ['годовая', 'итоговая', 'четверть']
good_value_of_estimate_type_name = ['работа', 'задание', 'диктант', 'тест', 'чтение', 'сочинение', 'изложение', 'опрос', 'зачёт']

def get_user_agent():
    with open('useragents/user_agent.txt') as f:
        user_agents = f.readlines()
        ua = random.choice(user_agents).strip()
    return ua

def chek_esimate_type_name(estimate_type_name):
    for good_value in good_value_of_estimate_type_name:
        if good_value in estimate_type_name.lower():
            return True
    return False


def get_marks_dict(response):
    marks = {}
    marks_info = response.get('data').get('items')
    for info_marks_all in marks_info:
        marks[info_marks_all['subject_name']] = {'q_marks': [],
                                                  'last_three': [],
                                                  'count_marks': [],
                                                  'average': [],
                                                  'final': []
                                                 }

    for subject_data in marks_info:
        estimate_value_name = subject_data['estimate_value_name']

        if str(estimate_value_name).lower() not in bad_estimate_value_name and estimate_value_name.lower() not in bad_estimate_type_name and chek_esimate_type_name(subject_data['estimate_type_name']):
            marks[subject_data['subject_name']]['q_marks'].append(int(estimate_value_name))

        else:
            for estimate_type_name_split in subject_data['estimate_type_name'].split():
                if estimate_type_name_split == 'четверть':
                    marks[subject_data['subject_name']]['final'].append(int(estimate_value_name))
    return marks


def register_and_save_cookies(user_id, ua):

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Access-Control-Allow-Origin': '*',
        'Connection': 'keep-alive',
        'Content-Type': 'text/plain',
        'Referer': 'https://dnevnik2.petersburgedu.ru/estimate',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-agent': ua,
        'X-KL-Ajax-Request': 'Ajax_Request',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
    }

    # options = webdriver.ChromeOptions()
    options = webdriver.FirefoxOptions()
    options.add_argument(f'user-agent={ua}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument(f'--proxy-server={random.choice(proxies)}')

    # driver = webdriver.Chrome(
    #     executable_path=EX_PATH_DRIVER,
    #     options=options
    # )

    driver = webdriver.Firefox(
        executable_path=os.getenv('EX_PATH_DRIVER'),
        options=options,
    )

    url = 'https://dnevnik2.petersburgedu.ru'

    login, password = db.get_login_and_password(user_id)[0], db.get_login_and_password(user_id)[1]
    try:
        driver.get(url=url)
        time.sleep(3)
        get_esia = driver.find_element(By.CLASS_NAME, 'button_size_m')
        driver.execute_script("arguments[0].click();", get_esia)
        time.sleep(5)
        email_esia = driver.find_element(By.ID, 'login')
        passw_esia = driver.find_element(By.ID, 'password')
        email_esia.send_keys(login)
        passw_esia.send_keys(password)
        driver.find_element(By.CLASS_NAME, 'plain-button_wide').click()
        pickle.dump(driver.get_cookies(), open(f'cookies/cookies{user_id}', 'wb'))
        params_group_id = {
            'p_page': '1'
        }

        cookies = {cookies_data['name']: str(cookies_data['value']) for cookies_data in pickle.load(open(f'cookies/cookies{user_id}', 'rb'))}

        name = db.get_name(user_id=user_id)[0]
        response_info = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list', params=params_group_id, cookies=cookies, headers=headers).json().get('data').get('items')
        students_info = None
        for data in response_info:
            if data.get('firstname') == name:
                students_info = data
                break
        group_id = students_info['educations'][0]['group_id']
        education_id = students_info['educations'][0]['education_id']
        db.set_group_id(user_id=user_id, group_id=group_id)
        db.set_education_id(user_id=user_id, education_id=education_id)
    except IndexError:
        ...
    finally:
        driver.quit()


def convert_cookies(user_id):
    cookies = {cookies_data['name']: str(cookies_data['value']) for cookies_data in pickle.load(open(f'cookies/cookies{user_id}', 'rb'))}
    return cookies


def get_data(quater, user_id, ua):
    if not os.path.exists(f'cookies/cookies{user_id}'):
        register_and_save_cookies(user_id, ua)
        cookies = convert_cookies(user_id=user_id)
        data = get_marks(quater=quater, cookies=cookies, user_id=user_id, ua=ua)
    else:
        cookies = convert_cookies(user_id=user_id)
        data = get_marks(quater, cookies, user_id=user_id, ua=ua)
    return data


def get_marks(quater, cookies, user_id, ua):
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ru,en;q=0.9',
        'Access-Control-Allow-Origin': '*',
        'Connection': 'keep-alive',
        'Content-Type': 'text/plain',
        'Referer': 'https://dnevnik2.petersburgedu.ru/estimate',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-agent': ua,
        'X-KL-Ajax-Request': 'Ajax_Request',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
    }

    group_id = db.get_group_id(user_id=user_id)[1]

    params_date_f_t = {
        'p_group_ids[]': group_id,
        'p_page': '1',
    }
    response_date_f_t = requests.get(f'https://dnevnik2.petersburgedu.ru/api/group/group/get-list-period', params=params_date_f_t, cookies=cookies, headers=headers).json().get('data').get('items')

    date_f = None
    date_t = None
    for data in response_date_f_t:
        if int(data['education_period'].get('code')) == int(quater):
            date_f = data.get('date_from')
            date_t = data.get('date_to')
            break

    p_educations = db.get_education_id(user_id=user_id)

    params = {
        'p_educations[]': p_educations,
        'p_date_from': date_f,
        'p_date_to': date_t,
        'p_limit': '100',
        'p_page': '1',
    }

    response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params,
                            cookies=cookies, headers=headers).json()

    marks = get_marks_dict(response=response)

    total_pages = response.get('data').get('total_pages')

    if total_pages > 2:
        for subject_page in range(2, total_pages + 1):
            params = {
                'p_educations[]': p_educations,
                'p_date_from': date_f,
                'p_date_to': date_t,
                'p_limit': '100',
                'p_page': subject_page,
            }

            response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params,
                                    cookies=cookies, headers=headers).json()
            marks_page = get_marks_dict(response=response)
            for sub, sub_data in marks_page.items():
                q_marks = sub_data[['q_marks'][0]]
                marks[sub]['q_marks'] = list(marks[sub]['q_marks']) + q_marks

    else:
        params = {
            'p_educations[]': p_educations,
            'p_date_from': date_f,
            'p_date_to': date_t,
            'p_limit': '100',
            'p_page': 2,
        }

        response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params,
                                cookies=cookies, headers=headers).json()
        marks_page = get_marks_dict(response=response)

        for sub, sub_data in marks_page.items():
            q_marks = sub_data[['q_marks'][0]]
            final_m = sub_data['final']
            marks[sub]['q_marks'] = list(marks[sub]['q_marks']) + q_marks
            if final_m:
                marks[sub]['final'] = final_m
    return marks


def sort_data(data, quater):
    for subject_info in data.copy():
        try:
            data_sub_info = data[subject_info]
            last_three = data[subject_info]['q_marks'][2::-1]
            count_marks = len(data[subject_info]['q_marks'])
            sum_marks = sum(data[subject_info]['q_marks'])

            data_sub_info['average'] = round(sum_marks / count_marks, 2)
            data_sub_info['last_three'] = last_three
            data_sub_info['count_marks'] = count_marks
        except ZeroDivisionError:
            del data[subject_info]

    if not data:
        data = f'Мы пока не нашли оценок по {quater} четверти'
        return data
    sort_result = dict(sorted(data.items()))
    if quater == 20:
        res = f'Год\n\n'
        for subject, sub_data in sort_result.items():
            res += f"{subject}: {sub_data['average']} ({sub_data['count_marks']})\n"
        res = res.replace('Основы безопасности жизнедеятельности', 'ОБЖ').replace('Изобразительное искусство', 'ИЗО').replace('Физическая культура', 'Физ-ра').replace('Иностранный язык (английский)', 'Английский язык').replace('История России. Всеобщая история', 'История')
    else:
        res = f'{quater} четверть\n\n'
        for subject, sub_data in sort_result.items():
            average = sub_data['average']
            count = sub_data['count_marks']
            final_m = ''
            if sub_data['final'][0]:
                final_m = '| ' + str(sub_data['final'][0])
            last_3 = ''
            for m in sub_data['last_three']:
                last_3 += str(m) + ' '
            res += f'{subject}: {average} ({count}) {last_3}{final_m}\n'
        res = res.replace('Основы безопасности жизнедеятельности', 'ОБЖ').replace('Изобразительное искусство', 'ИЗО').replace('Физическая культура', 'Физ-ра').replace('Иностранный язык (английский)', 'Английский язык').replace('История России. Всеобщая история', 'История')
    return res


def get_m_result(quater: int, user_id):
    # try:
    ua = get_user_agent()
    result: dict = get_data(user_id=user_id, quater=quater, ua=ua)
    res = sort_data(data=result, quater=quater)
    return res

    # except AttributeError:
    #     try:
    #         os.remove(f'cookies/cookies{user_id}')
    #     except FileNotFoundError:
    #         ...
    #
    #     finally:
    #         return 'Возможно вы указали не тот логин или пароль!\nПопробуйте ещё раз.'
    # except Exception:
    #     return 'Ошибка попробуйте позже.'
