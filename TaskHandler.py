from datetime import datetime
import json
import requests
from flask import Flask, request, make_response, jsonify


class TaskHandler:
    def __init__(self, response):
        self.responseId = response['responseId']
        self.queryText = response['queryResult']['queryText']
        self.parameters = response['queryResult']['parameters']
        self.taskType = response['queryResult']['intent']['displayName']
        with open('bot_config_private.json') as f:  # Use bot_config_private.json for development
            self.config = json.load(f)

    def handle(self):
        if self.taskType == 'weather' or self.taskType == 'weather - location':
            return self.handleWeather()
        elif self.taskType == 'waste classification':
            return self.hadnleWasteClassification()
        elif self.taskType == 'easter egg':
            return self.handleEasterEgg()
        else:
            return self._replyText("I don't know what to do.")

    # ==================================================================
    # Handling starts

    def handleWeather(self):

        def to_degree_celsius(degree_kelvin):
            return round(degree_kelvin - 273.1)

        if self.parameters['geo-city'] == '':
            return self._replyText('May I know which city we are talking about?')

        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}'.format(self.parameters['geo-city'],
                                                                                    self.config['open_weather_appid'])

        try:
            res = requests.get(url).json()
            weather_description = res['weather'][0]['description']
            temp = res['main']['temp']
            temp_max = res['main']['temp_max']
            temp_min = res['main']['temp_min']
        except Exception:
            return self._replyText("Sorry. I had a problem retrieving weather information.")

        reply = "It is {} in {}. The temperature is {} °C. The high will be {} °C. The low will be {} °C.".format(
            weather_description,
            self.parameters['geo-city'],
            to_degree_celsius(temp),
            to_degree_celsius(temp_max),
            to_degree_celsius(temp_min)
        )
        return self._replyText(reply)

    def hadnleWasteClassification(self):

        if self.parameters['Garbage'] == '':
            return self._replyText("Please provide the waste name in your query.")

        url = 'https://sffc.sh-service.com/wx_miniprogram/sites/feiguan/trashTypes_2/Handler/Handler.ashx?a=GET_KEYWORDS&kw={}'.format(self.parameters['Garbage'])

        try:
            res = requests.get(url).json()
            print(res)
            if res['kw_list'] == None:
                return self._replyText("Sorry. I'm not sure.")
            else:
                reply = ''
                for item in res['kw_arr']:
                    reply += "{} belongs to {}.\n".format(item['Name'], item['TypeKey'])
                return self._replyText(reply.strip('\n'))

        except Exception:
            return self._replyText("Sorry. I had a problem retrieving data.")


    def handleEasterEgg(self):
        time1 = datetime(2018, 7, 7)
        time2 = datetime.now()
        delta = time2 - time1
        return self._replyText(u'🐶🐱面面和佳佳已经在一起{}天啦！❤️❤️❤️'.format(delta.days))

    def _replyText(self, message):
        return jsonify({'fulfillmentText': message})
