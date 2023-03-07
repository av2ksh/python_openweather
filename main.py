
import telebot;
import requests;
import sys;
import os;
from dotenv import load_dotenv;
from io import StringIO
load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT'))
appid = os.getenv('APPID')
s_city_name = "Minsk"



def get_wind_direction(deg):
    l = ['С ','СВ',' В','ЮВ','Ю ','ЮЗ',' З','СЗ']
    for i in range(0,8):
        step = 45.
        min = i*step - 45/2.
        max = i*step + 45/2.
        if i == 0 and deg > 360-45/2.:
            deg = deg - 360
        if deg >= min and deg <= max:
            res = l[i]
            break
    return res

def get_city_id(s_city_name):
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/find",
                     params={'q': s_city_name, 'type': 'like', 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        cities = ["{} ({})".format(d['name'], d['sys']['country'])
                  for d in data['list']]
        city_id = data['list'][0]['id']
    except Exception as e:
        print("Exception (find):", e)
        pass
    assert isinstance(city_id, int)
    return city_id


def request_current_weather(city_id):
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                     params={'id': get_city_id(s_city_name), 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        print("conditions:", data['weather'][0]['description'])
        print("temp:", data['main']['temp'])
        print("temp_min:", data['main']['temp_min'])
        print("temp_max:", data['main']['temp_max'])
    except Exception as e:
        print("Exception (weather):", e)
        pass


def request_forecast(city_id):
    
    try:
        res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                           params={'id': get_city_id(s_city_name), 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        for i in data['list']:
                    print((i['dt_txt'])[5:16],'{0:+3.0f}'.format(i['main']['temp']),
                    '{0:2.0f}'.format(i['wind']['speed']) + " м/с",
                    get_wind_direction(i['wind']['deg']),
                    i['weather'][0]['description'])
    except Exception as e:
        print("Exception (forecast):", e)
        pass

def define_output(request_forecast):
    city_id = get_city_id(s_city_name)
    buffer = StringIO()
    sys.stdout = buffer
    print(request_forecast(city_id))
    sys.stdout = sys.__stdout__
    output = buffer.getvalue()
    output = output.replace('пасмурно', '☁️')
    output = output.replace('ясно', '☀️')
    output = output.replace('переменная облачность', '🌥')
    output = output.replace('небольшая облачность', '🌥')
    output = output.replace('облачно с прояснениями', '🌥')
    output = output.replace('небольшой снег', '🌨')
    output = output.replace('небольшой дождь', '🌦')
    output = output.replace('дождь', '🌧')
    output = output.replace('None', '')
    output = output.replace('снег', '🌨')
    return output

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global s_city_name
    if message.text == "/start":
       bot.send_message(message.from_user.id, "Введите название города, например Minsk:")
#       print(message.text, message.from_user.id)
    elif message.text == "/prognoz":
#       print(s_city_name)
       bot.send_message(message.from_user.id, "Прогноз для города " + s_city_name + ":\n" + define_output(request_forecast))
    else:
        try:
            s_city_name = message.text
            get_city_id(s_city_name)
            bot.send_message(message.from_user.id, "Принято! Такой город существует. Используйте /prognoz.")  
        except:
            bot.send_message(message.from_user.id, "Такого города нет в базе, введите название города, например Minsk:")

bot.polling(none_stop=True, interval=0)