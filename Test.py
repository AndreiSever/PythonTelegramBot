import unittest, datetime
from BotTelegramm import BotTelegramm
import tokens

class Test(unittest.TestCase):
    """
    Класс тестирования методов класса BotTelegramm.
    """
    def test_queryDB_select(self):
        """
        Проверяет запрос select к базе данных.
        """
        bot = BotTelegramm()
        res = bot.queryDB('','')
        actual = isinstance(res, list)
        self.assertEqual(actual, True)
    
    def test_queryDB_insert(self):
        """
        Проверяет запрос insert к базе данных.
        """
        bot = BotTelegramm()
        actual = bot.queryDB(29384, datetime.datetime.now())
        self.assertEqual(actual, False)

    def test_temperature(self):
        """
        Проверяет запрос к openweathermap.
        """
        bot = BotTelegramm()
        bot.TokenWeather = tokens.TokenWeather
        res = bot.temperature()
        self.assertEqual(isinstance(res, str), True)

    def test_telegramm(self):
        """
        Проверяет запроc к telegram.
        """
        bot = BotTelegramm()
        bot.TokenTelegramm = tokens.TelegrammToken
        res = bot.telegramm('getUpdates')
        actual =  isinstance(res, dict)
        self.assertEqual(actual, True)
    
    def test_telegramm_exec(self):
        """
        Проверяет запрос к telegramm в зависимости от текста сообщения.
        """
        bot = BotTelegramm()
        bot.TokenTelegramm = tokens.TelegrammToken
        bot.TokenWeather = tokens.TokenWeather
        chat = 561832271
        text = ['погода', '/start']
        for txt in text:
            res = bot.telegramm_exec(chat, txt)
            actual =  isinstance(res, dict)
            self.assertEqual(actual, True)


if __name__=='__main__':
    unittest.main()