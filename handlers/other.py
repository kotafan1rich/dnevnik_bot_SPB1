import pickle
import time
import requests
from db import Database
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

    finals_estimate_type_name = ['годовая', 'итоговая', 'четверть']

    def __init__(self, user_id: int, quater: str, login: str, password: str):
        self.user_id = user_id
        self.quater = self.QUATER_CODES[quater]
        self.login = login
        self.password = password
        

    def sort_marks(self, data: dict):
        return (
            self._sort_year(data)
            if self.quater == 20
            else self._sort_quater(data, data)
        )

    def _sort_quater(self, data, sort_result):
        print(data)
        finals_average = data['finals_average']
        result = f'{self.quater} четверть\n\n'
        for subject, sub_data in sort_result.items():
            if subject != 'finals_average':
                average = sub_data['average'][0]
                count = sub_data['count_marks'][0]
                final_m = ''
                if sub_data['final_q']:
                    final_m = '=> ' + str(sub_data['final_q'][0])
                last_3 = ' '.join(sub_data['last_three'])
                result += f'<i>{subject}</i>  {last_3} ({count})  <i>{average}</i> {final_m}\n'
        if finals_average:
            result += f'\nСр. балл аттестации - {finals_average}'
        return (
            result.replace('Основы безопасности жизнедеятельности', 'ОБЖ')
            .replace('Изобразительное искусство', 'ИЗО')
            .replace('Физическая культура', 'Физ-ра')
            .replace('Иностранный язык (английский)', 'Английский язык')
            .replace('История России. Всеобщая история', 'История')
        )

    def _sort_year(self, sort_result):
        result = 'Год\n\n'
        all_finals_q = sort_result['all_finals_q']
        all_finals_y = sort_result['all_finals_y']
        for subject, sub_data in sort_result.items():
            if subject not in ['all_finals_q', 'all_finals_y']:
                finals_q = ' '.join(map(str, sub_data['final_q'][::-1]))
                finals_y = "=> " + str(sub_data['final_years'][0]) if sub_data['final_years'] else ''
                final = "| " + str(sub_data['final'][0]) if sub_data['final'] else ''
                result += f"<i>{subject}</i>  {sub_data['average'][0]} ({sub_data['count_marks'][0]}) {finals_q} {finals_y} {final}\n"
        if all_finals_q:
            result += f'\nСр. балл годовой аттестации - {all_finals_q}'
        if all_finals_y:
            result += f'\nСр. балл итоговой аттестации - {all_finals_y}'
        return (
            result.replace('Основы безопасности жизнедеятельности', 'ОБЖ')
            .replace('Изобразительное искусство', 'ИЗО')
            .replace('Физическая культура', 'Физ-ра')
            .replace('Иностранный язык (английский)', 'Английский язык')
            .replace('История России. Всеобщая история', 'История')
            .replace('Иностранный язык (английский язык)', 'Английский язык')
        )


def delete_cookies(user_id):
    requests.delete(url='http://127.0.0.1:7000/api/v1/marks/', json={'user_id': user_id}, timeout=10)


def upload_data(user_id, login, password, name):
    payload = {'login': login,
                    'password': password,
                    'name': name,
                    'user_id': user_id}
    requests.post(url='http://127.0.0.1:7000/api/v1/marks/', json=payload, timeout=10)


def get_m_result(user_id: int, quater: str):
    login, password = db.get_login_and_password(user_id)
    mark = Marks(user_id=user_id, quater=quater, login=login, password=password)
    payload = {'user_id': user_id, 'quater': quater if quater != 'Год' else 5}
    marks = requests.get('http://127.0.0.1:7000/api/v1/marks/', json=payload, timeout=10).json().get('data')
    return mark.sort_marks(marks)
