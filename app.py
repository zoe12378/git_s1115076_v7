from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Line bot 相關設定
line_bot_api = LineBotApi('/ifIOXVIsQQPpwIukXv4QDZgA979eZSAC5G87k1JLKZnG0xSriHyC+xtydkAxVX0eKBXB/KyCdkMNx3oCm74xxjuxPFeKH8giQkrxaAP0XNNZG5wuxZ/66nfX0hqu9cj5WFofra4uEr0sbc6xXyyDgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('47250539de3b4c9b5f35c0c62ed15527')

# 使用者狀態記錄
user_state = {}

# 劇情流程設定
story = {
    "start": "你是一位探險家，進入了一座神秘的森林，面臨著未知的挑戰。你看到兩條小路，一條被藤蔓覆蓋，另一條光線充足。你選擇：\n\n1. 走進藤蔓覆蓋的小路\n2. 選擇光線充足的小路",
    "1": "你踏入藤蔓小路，四周變得越來越黑暗。隱約間，你聽到低語聲，像是有人在訴說著故事。你選擇：\n\n1. 繼續前行\n2. 決定返回入口",
    "2": "你選擇光線充足的小路，一路順利走出森林。結局：平安無事。\n請輸入「再來一局」開始新遊戲。",
    "1-1": "你來到了寶藏房間，但地板開始塌陷！你選擇：\n\n1. 跳向寶藏\n2. 立刻逃跑",
    "1-2": "你選擇返回入口，錯過了探索的機會。結局：安全的放棄。\n請輸入「再來一局」開始新遊戲。",
    "1-1-1": "你成功拿到了寶藏，但地板完全塌陷，你被困在裡面。結局：寶藏的囚徒。\n請輸入「再來一局」開始新遊戲。",
    "1-1-2": "你快速逃離了房間，雖然沒拿到寶藏，但安全回到了森林入口。結局：理智的撤退。\n請輸入「再來一局」開始新遊戲。"
}

# 重置遊戲函式
def reset_game(user_id):
    user_state[user_id] = "start"

# 獲取使用者選擇
def get_choice(event, reply_token, valid_choices):
    user_input = event.message.text.strip()
    if user_input in valid_choices:
        return user_input
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入1 or 2"))
        return None  # 無效輸入，需要重新要求輸入

# 依據使用者選擇進行場景切換
def handle_story(event, user_id):
    state = user_state.get(user_id, "start")
    user_input = get_choice(event, event.reply_token, ["1", "2"])

    if user_input:
        if state == "start":
            if user_input == "1":
                user_state[user_id] = "1"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["1"]))
            elif user_input == "2":
                user_state[user_id] = "2"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["2"]))
                reset_game(user_id)

        elif state == "1":
            if user_input == "1":
                user_state[user_id] = "1-1"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["1-1"]))
            elif user_input == "2":
                user_state[user_id] = "1-2"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["1-2"]))
                reset_game(user_id)

        elif state == "1-1":
            if user_input == "1":
                user_state[user_id] = "1-1-1"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["1-1-1"]))
                reset_game(user_id)
            elif user_input == "2":
                user_state[user_id] = "1-1-2"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["1-1-2"]))
                reset_game(user_id)

# 開始遊戲時由系統主動發話
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_input = event.message.text.lower()

    # 檢查遊戲結束後輸入非「再來一局」時的提醒
    if user_input == "再來一局":
        reset_game(user_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["start"]))
    elif user_state.get(user_id, "start") == "start":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=story["start"]))
        user_state[user_id] = "start"
    else:
        if user_state.get(user_id) in ["2", "1-2", "1-1-1", "1-1-2"]:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入「再來一局」開始新遊戲"))
        else:
            handle_story(event, user_id)

if __name__ == "__main__":
    reset_game('default')  # 初始化一個預設使用者
    # 指定端口為 8080
    app.run(debug=True, host="0.0.0.0", port=8080)
