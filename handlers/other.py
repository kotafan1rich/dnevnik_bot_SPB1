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

class Marks:
    QUATER_CODES = {
        '1': 1,
        '2': 2,
        '3': 3,
        '4': 4,
        'Год': 20
    }

    bad_estimate_value_name = ['замечание', 'неизвестная', 'по болезни', 'зачёт']
    bad_estimate_type_name = ['годовая', 'итоговая', 'четверть', 'посещаемость']
    finals_estimate_type_name = ['годовая', 'итоговая', 'четверть']
    good_value_of_estimate_type_name = ['работа', 'задание', 'диктант', 'тест', 'чтение', 'сочинение', 'изложение', 'опрос', 'зачёт']


    def __init__(self, user_id: int, quater: str, login: str, password: str):
        self.user_id = user_id
        self.quater = self.QUATER_CODES[quater]
        self.login = login
        self.password = password
        self.group_id = None
        self.education_id = None
        self.cookies = None
        self.user_agent = None
        self.date_f = None
        self.date_t = None
        self.p_periods = None
        self.headers = None

    def chek_esimate_type_name(self, estimate_type_name: str):
        for good_value in self.good_value_of_estimate_type_name:
            if good_value in estimate_type_name.lower():
                return True
        return False

    def sort_marks(self, data: dict):
        for subject_info in data.copy():
            try:
                data_sub_info = data[subject_info]
                last_three = list(map(str, data[subject_info]['q_marks'][2::-1]))
                count_marks = len(data[subject_info]['q_marks'])
                sum_marks = sum(data[subject_info]['q_marks'])
                data_sub_info['average'] = round(sum_marks / count_marks, 2)
                data_sub_info['last_three'] = last_three
                data_sub_info['count_marks'] = count_marks
            except ZeroDivisionError:
                del data[subject_info]
        if not data:
            return f'Мы пока не нашли оценки за {self.quater}-ую четверть'
        sort_result = dict(sorted(data.items()))

        if self.quater == 20:
            res = f'Год\n\n'
            all_finals_q = [i['final_years'] for i in sort_result.values() if i['final_years']]
            all_finals_y = [i['final'] for i in sort_result.values() if i['final']]
            finals_q_averge = round(sum(all_finals_q) / len(all_finals_q), 2) if all_finals_q else None
            finals_y_averge = round(sum(all_finals_y) / len(all_finals_y), 2) if all_finals_y else None
            for subject, sub_data in sort_result.items():
                finals_q = ' '.join(map(str, sub_data['final_q'][::-1]))
                finals_y = "=> " + str(sub_data['final_years']) if sub_data['final_years'] else ''
                final = f"| " + str(sub_data['final']) if sub_data['final'] else ''
                res += f"<i>{subject}</i>  {sub_data['average']} ({sub_data['count_marks']}) {finals_q} {finals_y} {final}\n"
            if finals_q_averge:
                res += f'\nСр. балл годовой аттестации - {finals_q_averge}'
            if finals_y_averge:
                res += f'\nСр. балл итоговой аттестации - {finals_q_averge}'
            res = res.replace('Основы безопасности жизнедеятельности', 'ОБЖ').replace('Изобразительное искусство','ИЗО').replace('Физическая культура', 'Физ-ра').replace('Иностранный язык (английский)', 'Английский язык').replace('История России. Всеобщая история', 'История').replace('Иностранный язык (английский язык)', 'Английский язык')
        else:
            all_finals = [marks_info['final_q'][0] for marks_info in data.values() if bool(marks_info['final_q'])]
            finals_averge = round(sum(all_finals) / len(all_finals), 2) if all_finals else None
            res = f'{self.quater} четверть\n\n'
            for subject, sub_data in sort_result.items():
                average = sub_data['average']
                count = sub_data['count_marks']
                final_m = ''
                if sub_data['final_q']:
                    final_m = '=> ' + str(sub_data['final_q'][0])
                last_3 = ' '.join(sub_data['last_three'])
                res += f'<i>{subject}</i>  {last_3} ({count})  <i>{average}</i> {final_m}\n'
            if finals_averge:
                res += f'\nСр. балл аттестации - {finals_averge}'
            res = res.replace('Основы безопасности жизнедеятельности', 'ОБЖ').replace('Изобразительное искусство','ИЗО').replace('Физическая культура', 'Физ-ра').replace('Иностранный язык (английский)', 'Английский язык').replace('История России. Всеобщая история', 'История')
        return res

    def get_marks_dict(self, response: dict, marks: dict):
        bad_estimate_value_name = self.bad_estimate_value_name
        bad_estimate_type_name = self.bad_estimate_type_name
        marks_info = response.get('data').get('items')

        for subject_data in marks_info:
            estimate_value_name = subject_data['estimate_value_name']

            if str(estimate_value_name).lower() not in bad_estimate_value_name and estimate_value_name.lower() not in bad_estimate_type_name and self.chek_esimate_type_name(subject_data['estimate_type_name']):
                marks[subject_data['subject_name']]['q_marks'].append(int(estimate_value_name))

            else:
                for estimate_type_name_split in subject_data['estimate_type_name'].split():
                    if estimate_type_name_split in ['четверть',]:
                        marks[subject_data['subject_name']]['final_q'].append(int(estimate_value_name))
                    elif estimate_type_name_split in ['Годовая']:
                        marks[subject_data['subject_name']]['final_years'] = int(estimate_value_name)
                    elif estimate_type_name_split in ['Итоговая']:
                        marks[subject_data['subject_name']]['final'] = int(estimate_value_name)

        return marks

    def save_cookies(self):
        if not os.path.exists(f'cookies/cookies{self.user_id}'):
            with open('useragents/user_agent.txt') as f:
                user_agents = f.readlines()
                ua = random.choice(user_agents).strip()
            self.user_agent = ua
            self.headers = {
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

            try:
                driver.get(url=url)
                time.sleep(3)
                get_esia = driver.find_element(By.CLASS_NAME, 'button_size_m')
                driver.execute_script("arguments[0].click();", get_esia)
                time.sleep(5)
                email_esia = driver.find_element(By.ID, 'login')
                passw_esia = driver.find_element(By.ID, 'password')
                email_esia.send_keys(self.login)
                passw_esia.send_keys(self.password)
                driver.find_element(By.CLASS_NAME, 'plain-button_wide').click()
                time.sleep(3)
                driver.find_element(By.CLASS_NAME, 'plain-button-inline').click()
                time.sleep(3)
                pickle.dump(driver.get_cookies(), open(f'cookies/cookies{self.user_id}', 'wb'))
                params_group_id = {
                    'p_page': '1'
                }

                cookies = {cookies_data['name']: str(cookies_data['value']) for cookies_data in pickle.load(open(f'cookies/cookies{self.user_id}', 'rb'))}
                name = db.get_name(user_id=self.user_id)[0]
                response_info = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/person/related-child-list', params=params_group_id, cookies=cookies, headers=self.headers).json().get('data').get('items')
                students_info = None
                for data in response_info:
                    if data.get('firstname') == name:
                        students_info = data
                        break

                group_id = students_info['educations'][0]['group_id']
                education_id = students_info['educations'][0]['education_id']
                db.set_group_id(user_id=self.user_id, group_id=group_id)
                db.set_education_id(user_id=self.user_id, education_id=education_id)
                self.cookies = cookies

            except TypeError:
                ...
            finally:
                driver.quit()
        else:
            with open('useragents/user_agent.txt') as f:
                user_agents = f.readlines()
                ua = random.choice(user_agents).strip()


            self.user_agent = ua
            cookies = {cookies_data['name']: str(cookies_data['value']) for cookies_data in
                       pickle.load(open(f'cookies/cookies{self.user_id}', 'rb'))}

            self.cookies = cookies


    def get_cookies(self):
        cookies = {cookies_data['name']: str(cookies_data['value']) for cookies_data in
                   pickle.load(open(f'cookies/cookies{self.user_id}', 'rb'))}
        return cookies

    def set_marks_params(self):
        cookies = self.cookies
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru,en;q=0.9',
            'Access-Control-Allow-Origin': '*',
            'Connection': 'keep-alive',
            'Content-Type': 'text/plain',
            'Referer': 'https://dnevnik2.petersburgedu.ru/estimate',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-agent': self.user_agent,
            'X-KL-Ajax-Request': 'Ajax_Request',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            'sec-ch-ua-mobile': '?0',
        }

        group_id = db.get_group_id(self.user_id)[1]

        params_date_f_t = {
            'p_group_ids[]': group_id,
            'p_page': '1',
        }
        response_date_f_t = requests.get(f'https://dnevnik2.petersburgedu.ru/api/group/group/get-list-period', params=params_date_f_t, cookies=cookies, headers=self.headers).json().get('data').get('items')

        for data in response_date_f_t:
            if int(data['education_period'].get('code')) == int(self.quater):

                self.date_f = data.get('date_from')
                self.date_t = data.get('date_to')
                self.p_periods = str(data.get('identity').get('id'))
                break

    def get_marks(self):
        p_educations = db.get_education_id(self.user_id)[0]
        p_groups = db.get_group_id(self.user_id)[1]
        params = {
            'p_educations[]': p_educations,
            'p_date_from': self.date_f,
            'p_date_to': self.date_t,
            'p_limit': '100',
            'p_page': '1',
        }

        response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params, cookies=self.cookies, headers=self.headers).json()

        params_list_subjects = {
            'p_limit': '100',
            'p_page': '1',
            'p_educations[]': p_educations,
            'p_groups[]': p_groups,
            'p_periods[]': self.p_periods,
        }
        list_subjects = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/subject/list-studied',params=params_list_subjects,cookies=self.cookies,headers=self.headers).json().get('data').get('items')

        marks = {}
        for info_marks_all in list_subjects:
            marks[info_marks_all['name']] = {'q_marks': [],
                                                     'last_three': [],
                                                     'count_marks': [],
                                                     'average': [],
                                                     'final_q': [],
                                                     'final_years': None,
                                                     'final': None
                                                     }

        marks = self.get_marks_dict(response=response, marks=marks)

        total_pages = response.get('data').get('total_pages')

        if total_pages > 1:
            for subject_page in range(2, total_pages + 1):
                params = {
                    'p_educations[]': p_educations,
                    'p_date_from': self.date_f,
                    'p_date_to': self.date_t,
                    'p_limit': '100',
                    'p_page': subject_page,
                }

                response = requests.get('https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', params=params,
                                        cookies=self.cookies, headers=self.headers).json()
                marks = self.get_marks_dict(response=response, marks=marks)

        return marks


def get_m_result(user_id: int, quater: str):
    login, password = db.get_login_and_password(user_id)
    mark = Marks(user_id=user_id, quater=quater, login=login, password=password)
    mark.save_cookies()
    mark.set_marks_params()
    not_sort_m = mark.get_marks()
    marks = mark.sort_marks(not_sort_m)
    return marks

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
