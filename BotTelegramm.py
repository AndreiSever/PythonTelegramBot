import sqlite3
import datetime
import json
import time
import requests

class BotTelegramm:
    """
    Класс BotTelegramm.
    """
    def __init__(self):
        """
        Инициализирует переменные.

        Атрибуты
        --------
        TokenTelegramm : string
            Токен telegramm. (Значение '')
        TokenWeather : string
            Токен openweathermap. (Значение '')
        update : int
            id последнего обновления сообщения telegramm. (Значение 0)
        """
        self.TokenTelegramm = ''
        self.TokenWeather = ''
        self.update = 0

    def queryDB(self, user, date):
        """
        Делает запрос к базе данных.

        Параметры
        ---------
        user : int
            id пользователя.
        date : date_time
            Время обращения.
        
        Возврат
        -------
        info : array_like
            Массив с выборкой из базы данных.
        bool
            Возвращает False при вставке в базу данных.
        bool
            Возвращает True при ошибке.

        Ошибки
        ------
        sqlite3.Error
            Возникает при создании, подключении или чтении базы данных.
        """
        try:
            conn = sqlite3.connect('base/information.db')
            curs = conn.cursor()
            if user=='':
                curs.execute('''CREATE TABLE if not exists toData (id int auto_increment primary key, user int, date datetime)''')
                curs.execute("SELECT user, date  FROM toData")
                info = curs.fetchall()
            else:
                curs.execute(f"INSERT INTO toData (user, date) VALUES (?,?)", (user, date))
                conn.commit()
            curs.close()
            conn.close()
            if user=='':
                return info 
            else:
                return False
        except sqlite3.Error as err:
            print(err)
            return True
    
    def showDB(self):
        """
        Выводит информацию из базы данных.

        Возврат
        -------
        bool
            Возвращает False.
        bool
            Возвращает True при ошибке.
        """
        data = self.queryDB('','')
        if data == False:
            return True
        else:
            for i in data:
                print('Пользователь: ', i[0], 'Обращался: ', i[1])
            return False

    def temperature(self):
        """
        Делает запрос к openweathermap.

        Возврат
        -------
        string
            Температура.
        bool
            Возвращает False при ошибке.

        Ошибки
        ------
        requests.exceptions.RequestException
            Возникает при отправке get запроса.
        Exception
            Возникает при обращении по ключю в словаре.
        r.status_code
            Возникает если запрос выполнен не успешно.
        """
        url = f'http://api.openweathermap.org/data/2.5/weather?lat=55.15&lon=61.43&appid={self.TokenWeather}&units=metric'
        try:
            r = requests.get(url)
            if r.status_code == 200:
                try:
                    data = r.json()
                    temp = data['main']['temp']
                    return f"Температура в Челябинске {temp} °C"
                except Exception as err:
                    print(err)
                    return False
            else:
                print(r.text)
                return False
        except requests.exceptions.RequestException as err:
            print(err)
            return False

    def telegramm(self, do):
        """
        Делает запрос к telegramm.

        Параметры
        ---------
        do : string
            Параметры для вставки в ссылки запроса.
        
        Возврат
        -------
        array_like
            Ответ от сервера.
        bool
            Возвращает False если ошибка.

        Ошибки
        ------
        requests.exceptions.RequestException
            Возникает при отправке get запроса.
        r.status_code
            Возникает если не существует метода.
        """
        url = f'https://api.telegram.org/bot{self.TokenTelegramm}/{do}'
        try:
            r = requests.get(url, proxies={"https": 'http://207.180.233.72:80'})
            if r.status_code == 200:
                return r.json()
            else:
                print(r.text)
                return False
        except requests.exceptions.RequestException as err:
            print(err)
            return False

    def telegramm_exec(self, chat, text):
        """
        Выполняет запрос к telegramm в зависимости от текста сообщения.

        Параметры
        ---------
        chat : int
            id чата.
        text : string
            Текста сообщения.
        
        Возврат
        -------
        answer : array_like
            Статус запроса к телеграмм.
        bool
            Возвращает True, если команда не была найдена.
        bool
            Возвращает False при неверном запросе.

        """
        if text == '/start':
            answer = self.telegramm(f'sendMessage?chat_id={chat}&text=Используете слово погода')
            if answer:
                return answer
            else:
                return False
        if ('погода' in text):
            temp =  self.temperature()
            if temp:
                answer = self.telegramm(f'sendMessage?chat_id={chat}&text={temp}')
                if answer:
                    return answer
                else:
                    return False
            else:
                return False
        return True


    def main(self):
        """
        Основная функция.

        Ошибки
        ------
        Exception
            Возникает при обращении по ключю в словаре.
        OSError
            Возникает, если произошла сетевая ошибка.
        IOError
            Возникает при ошибке чтения файла.
        """
        try:
            tokens = {}
            exec(open('tokens.py').read(), tokens)
            self.TokenTelegramm = tokens['TelegrammToken']
            self.TokenWeather = tokens['TokenWeather']
            if self.showDB():
                return
            while True:
                update = self.telegramm('getUpdates')
                if not update:
                    return
                if len(update['result']) == 0:
                    continue 
                result = update['result'][-1]
                if self.update != result['update_id']:
                    self.update = result['update_id']
                    try:
                        user = result['message']['from']['id']
                        chat = result['message']['chat']['id']
                        text = result['message']['text']
                    except Exception:
                        user = result['edited_message']['from']['id']
                        chat = result['edited_message']['chat']['id']
                        text = result['edited_message']['text']

                    data = self.queryDB(user, datetime.datetime.now())
                    if data:
                        return
                    answer = self.telegramm_exec(chat, text.lower())
                    if not answer:
                        return
                time.sleep(2)
        except (OSError,IOError) as err:
            print(err)
            return


if __name__ == '__main__':
    bot = BotTelegramm()
    bot.main()