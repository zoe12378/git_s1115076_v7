from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 替換成你的 Line Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi('/ifIOXVIsQQPpwIukXv4QDZgA979eZSAC5G87k1JLKZnG0xSriHyC+xtydkAxVX0eKBXB/KyCdkMNx3oCm74xxjuxPFeKH8giQkrxaAP0XNNZG5wuxZ/66nfX0hqu9cj5WFofra4uEr0sbc6xXyyDgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('47250539de3b4c9b5f35c0c62ed15527')

# 用來儲存用戶的遊戲進度
user_state = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 遊戲流程
def start_game(user_id):
    user_state[user_id] = 'start'
    return "你是一位探險家，進入了一座神秘的森林，面臨著未知的挑戰。\n1. 走進藤蔓覆蓋的小路\n2. 選擇光線充足的小路"

def scene_2():
    return "你踏入藤蔓小路，四周變得越來越黑暗。隱約間，你聽到低語聲，像是有人在訴說著故事。\n1. 繼續前行\n2. 決定返回入口"

def scene_3():
    return "你走在光線充足的小路，來到了一片空曠的草地。\n1. 走向陰暗的洞穴\n2. 選擇明亮的出口"

def scene_4():
    return "你來到了寶藏房間，滿是財富。\n1. 冒險跳向寶藏\n2. 逃跑"

def scene_5():
    return "你選擇返回入口，錯過了探索的機會。\n結局：安全的放棄"

def scene_6():
    return "你來到了美麗的田野，生活平靜幸福。\n結局：平靜的生活"

def ending_1():
    return "你成為了傳奇冒險家，帶回了無價之寶。"

def ending_2():
    return "你逃跑了，保住了性命，但失去了寶藏。"

# 處理用戶訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    if user_id not in user_state:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=start_game(user_id)))
        return

    # 根據用戶的選擇更新遊戲進度
    if user_state[user_id] == 'start':
        if text == '1':
            user_state[user_id] = 'scene_2'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=scene_2()))
        elif text == '2':
            user_state[user_id] = 'scene_3'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=scene_3()))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇 1 或 2。"))

    elif user_state[user_id] == 'scene_2':
        if text == '1':
            user_state[user_id] = 'scene_4'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=scene_4()))
        elif text == '2':
            user_state[user_id] = 'scene_5'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=scene_5()))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇 1 或 2。"))

    elif user_state[user_id] == 'scene_3':
        if text == '1':
            user_state[user_id] = 'scene_4'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=scene_4()))
        elif text == '2':
            user_state[user_id] = 'scene_6'
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=scene_6()))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇 1 或 2。"))

    elif user_state[user_id] == 'scene_4':
        if text == '1':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ending_1()))
        elif text == '2':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ending_2()))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇 1 或 2。"))

    elif user_state[user_id] == 'scene_5' or user_state[user_id] == 'scene_6':
        # 遊戲結束，重置狀態
        del user_state[user_id]
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="遊戲結束。重新開始請輸入任何訊息。"))


if __name__ == "__main__":
    # 指定端口為 8080
    app.run(debug=True, host="0.0.0.0", port=8080)
