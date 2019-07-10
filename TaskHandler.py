import json
import requests
from flask import Flask, request, make_response, jsonify


class TaskHandler:
    def __init__(self, response):
        self.responseId = response['responseId']
        self.queryText = response['queryResult']['queryText']
        self.parameters = response['queryResult']['parameters']
        self.taskType = response['queryResult']['intent']['displayName']
        with open('bot_config.json') as f:
            self.config = json.load(f)

    def handle(self):
        if self.taskType == 'weather' or self.taskType == 'weather - location':
            return self.handleWeather()
        else:
            return self._replyText("I don't know what to do.")

    def handleWeather(self):

        def to_degree_celsius(degree_kelvin):
            return round(degree_kelvin - 273.1)

        if self.parameters['geo-city'] == '':
            return self._replyText('May I know which city we are talking about?')

        url = 'http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}'.format(self.parameters['geo-city'],
                                                                                    self.config['OPEN_WEATHER_APPID'])

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

    def _replyText(self, message):
        return jsonify({'fulfillmentText': message})
