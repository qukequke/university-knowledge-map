from flask import Flask, make_response, request
from chatbot_graph import ChatBotGraph

handler = ChatBotGraph()

app = Flask(__name__)


@app.after_request
def af_request(*resp_raw):
    resp = make_response(*resp_raw)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp



@app.route('/', methods=['GET', 'POST'])
def a():
    print(request.json)
    data = request.json
    if not data:
        return ''
    text = data['text']['content'].strip()
    user = data['senderNick']
    user_id = user
    print(text)
    answer = handler.chat_main(text, user_id)
    resp_text = {
        "at": {
            "atUserIds": [
                user_id
            ],
            "isAtAll": False
        },
        "msgtype": "markdown",
        "markdown": {
            "title": "快来问我啊",
            "text": answer,
        },
    }
    print(resp_text)
    return resp_text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=30000, debug=False)