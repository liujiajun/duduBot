from flask import Flask, request, make_response, jsonify
from TaskHandler import TaskHandler

app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello!'


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    return make_response(handleRequest())


def handleRequest():
    req = request.get_json(force=True)
    print(req)
    task_handler = TaskHandler(req)

    return task_handler.handle()


if __name__ == '__main__':
    app.run()
