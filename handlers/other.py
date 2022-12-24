# import datetime
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


estimate_type_name_value = ['работа', 'задание', 'диктант', 'тест', 'чтение', 'сочинение', 'изложение', 'опрос']
good_value_of_estimate_type_name = []
for i in estimate_type_name_value:
    good_value_of_estimate_type_name.append(i)
    good_value_of_estimate_type_name.append(f'{i[0].upper()}{i[1:]}')

ua = [
    'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)',
    'Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.13 (KHTML, like Gecko) Chrome/24.0.1290.1 Safari/537.13',
    'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5355d Safari/8536.25'
]


# proxies = ['89.107.197.165:3128', '89.108.74.82:1080']
def chek_esimate_type_name(estimate_type_name):
    s = 0
    for good_value in good_value_of_estimate_type_name:
        if good_value in estimate_type_name.split():
            s += 1
        if s == 1:
            return True
    return False


def register_and_save_cookies(user_id):
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
        'User-agent': random.choice(ua),
        'X-KL-Ajax-Request': 'Ajax_Request',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
    }

    # options = webdriver.ChromeOptions()
    options = webdriver.FirefoxOptions()
    options.add_argument(f'user-agent={random.choice(ua)}')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    # options.add_argument(f'--proxy-server={random.choice(proxies)}')

    # driver = webdriver.Chrome(
    #     executable_path=EX_PATH,
    #     options=options
    # )

    driver = webdriver.Firefox(
        executable_path=os.getenv('EX_PATH_DRIVER'),
        options=options,
    )

    url = 'https://dnevnik2.petersburgedu.ru'
    # url1 = 'https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html'

    login, password = db.get_login_and_password(user_id)[0], db.get_login_and_password(user_id)[1]
    # print(login)
    #
    # print(password)
    driver.get(url=url)
    time.sleep(1)
    get_esia = driver.find_element(By.CLASS_NAME, 'button_size_m')
    driver.execute_script("arguments[0].click();", get_esia)
    time.sleep(3)
    email_esia = driver.find_element(By.ID, 'login')
    passw_esia = driver.find_element(By.ID, 'password')
    email_esia.send_keys(login)
    passw_esia.send_keys(password)
    driver.find_element(By.CLASS_NAME, 'plain-button_wide').click()
    time.sleep(2)
    pickle.dump(driver.get_cookies(), open(f'cookies/cookies{user_id}', 'wb'))
    # driver.get('https://dnevnik2.petersburgedu.ru/estimate')
    params_group_id = {
        'p_page': '1',
        'p_jurisdictions[]': '4',
        'p_institutions[]': '1376',
    }

    for cookie in pickle.load(open(f'cookies/cookies{user_id}', 'rb')):
        driver.add_cookie(cookie)
    cookies = {}
    for cookies_data in pickle.load(open(f'cookies/cookies{user_id}', 'rb')):
        cookies[cookies_data['name']] = str(cookies_data['value'])

    group_id = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/group/related-group-list', params=params_group_id, cookies=cookies, headers=headers).json().get('data').get('items')[0].get('id')
    db.set_group_id(user_id=user_id, group_id=group_id)


def convert_cookies(user_id):
    cookies = {}
    for cookies_data in pickle.load(open(f'cookies/cookies{user_id}', 'rb')):
        cookies[cookies_data['name']] = str(cookies_data['value'])
    return cookies


def get_data(quater, user_id):
    if not os.path.exists(f'cookies/cookies{user_id}'):
        register_and_save_cookies(user_id)
        cookies = convert_cookies(user_id=user_id)
        data = get_marks(quater=quater, cookies=cookies, user_id=user_id)
    else:
        cookies = convert_cookies(user_id=user_id)
        data = get_marks(quater, cookies, user_id=user_id)
    return data


def get_marks(quater, cookies, user_id):
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
        'User-agent': random.choice(ua),
        'X-KL-Ajax-Request': 'Ajax_Request',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
        'sec-ch-ua-mobile': '?0',
    }

    params = {
        'p_page': '1',
    }
    group_id = db.get_group_id(user_id=user_id)

    params_date_f_t = {
        'p_group_ids[]': group_id,
        'p_page': '1',
    }

    response_date_f_t = requests.get('https://dnevnik2.petersburgedu.ru/api/group/group/get-list-period', params=params_date_f_t, cookies=cookies, headers=headers).json().get('data').get('items')[quater - 1]
    date_f = response_date_f_t.get('date_from')
    date_t = response_date_f_t.get('date_to')

    p_educations_response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list', params=params, cookies=cookies, headers=headers).json()
    p_educations = p_educations_response.get('data').get('items')[0].get('educations')[0].get('education_id')

    params = {
        'p_educations[]': p_educations,
        'p_date_from': date_f,
        'p_date_to': date_t,
        'p_limit': '100',
        'p_page': '1',
    }

    response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params,
                            cookies=cookies, headers=headers).json()

    marks = {}
    marks_info = response.get('data').get('items')
    for info_marks_all in marks_info:
        marks[info_marks_all['subject_name']] = []

    for subject_info in marks_info:
        if subject_info['estimate_value_name'] != 'Замечание':
            if 'Годовая' not in subject_info['estimate_type_name'] and 'Итоговая' not in subject_info['estimate_type_name'] and 'четверть' not in subject_info['estimate_type_name'] and 'Посещаемость' not in subject_info['estimate_type_name']:
                if chek_esimate_type_name(subject_info['estimate_type_name']) and subject_info['estimate_value_name'] != 'Зачёт':
                    marks[subject_info['subject_name']].append(int(subject_info['estimate_value_name']))

    total_pages = response.get('data').get('total_pages')

    if int(total_pages) > 1:
        if total_pages > 2:
            for subject_info in range(2, total_pages + 1):
                params = {
                    'p_educations[]': p_educations,
                    'p_date_from': date_f,
                    'p_date_to': date_t,
                    'p_limit': '100',
                    'p_page': subject_info,
                }

                response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params,
                                        cookies=cookies, headers=headers).json()
                marks_info = response.get('data').get('items')

                for subject_info_1 in marks_info:
                    if subject_info_1['estimate_value_name'] != 'Замечание':
                        if 'Годовая' not in subject_info_1['estimate_type_name'] and 'Итоговая' not in subject_info_1['estimate_type_name'] and 'четверть' not in subject_info_1['estimate_type_name'] and 'Посещаемость' not in subject_info_1['estimate_type_name']:
                            if chek_esimate_type_name(subject_info_1['estimate_type_name']) and subject_info_1['estimate_value_name'] != 'Зачёт':
                                marks[subject_info_1['subject_name']].append(int(subject_info_1['estimate_value_name']))
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
            marks_info = response.get('data').get('items')

            for subject_info_1 in marks_info:
                if subject_info_1['estimate_value_name'] != 'Замечание':
                    if 'Годовая' not in subject_info_1['estimate_type_name'] and 'Итоговая' not in subject_info_1['estimate_type_name'] and 'четверть' not in subject_info_1['estimate_type_name'] and 'Посещаемость' not in subject_info_1['estimate_type_name']:
                        if chek_esimate_type_name(subject_info_1['estimate_type_name']) and subject_info_1['estimate_value_name'] != 'Зачёт':
                            marks[subject_info_1['subject_name']].append(int(subject_info_1['estimate_value_name']))

    data = {'data': marks}

    return data


def sort_data(data, quater):
    for subject_info in data.copy():
        try:
            count_marks = len(data[subject_info])
            sum_marks = sum(data[subject_info])

            data[subject_info] = [round(sum_marks / count_marks, 2), count_marks]
        except ZeroDivisionError:
            del data[subject_info]

    if data == {}:
        data = 'нет оценок'
    sort_result = dict(sorted(data.items()))
    if quater == 5:
        res = f'Год\n\n'
        for subject, j in sort_result.items():
            res += f'{subject}: {j[0]} ({j[1]})\n'
        res = res.replace('Основы безопасности жизнедеятельности', 'ОБЖ').replace('Изобразительное искусство',
                                                                                  'ИЗО')
    else:
        res = f'{quater} четверть\n\n'
        for subject, j in sort_result.items():
            res += f'{subject}: {j[0]} ({j[1]})\n'
        res = res.replace('Основы безопасности жизнедеятельности', 'ОБЖ').replace('Изобразительное искусство',
                                                                                  'ИЗО')
    return res


def get_m_result(quater: int, user_id):
    if quater == 1:
        result: dict = get_data(user_id=user_id, quater=quater).get('data')
        if result == 'нет оценок':
            res = 'Нет оценок'
        else:
            res = sort_data(data=result, quater=quater)
        return res

    elif quater == 2:
        result: dict = get_data(quater=quater, user_id=user_id).get('data')
        if result == 'нет оценок':
            res = 'Нет оценок'
        else:
            res = sort_data(data=result, quater=quater)
        return res
    elif quater == 3:
        result: dict = get_data(quater=quater, user_id=user_id).get('data')
        if result == 'нет оценок':
            res = 'Нет оценок'
        else:
            res = sort_data(data=result, quater=quater)
        return res
    elif quater == 4:
        result: dict = get_data(quater=quater, user_id=user_id).get('data')
        if result == 'нет оценок':
            res = 'Нет оценок'
        else:
            res = sort_data(data=result, quater=quater)
        return res
    else:
        result: dict = get_data(quater=5, user_id=user_id).get('data')
        if result == 'нет оценок':
            res = 'Нет оценок'
        else:
            res = sort_data(data=result, quater=quater)
        return res
