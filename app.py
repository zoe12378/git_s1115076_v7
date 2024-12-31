from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from flask import Flask, request, abort

app = Flask(__name__)

line_bot_api = LineBotApi('/ifIOXVIsQQPpwIukXv4QDZgA979eZSAC5G87k1JLKZnG0xSriHyC+xtydkAxVX0eKBXB/KyCdkMNx3oCm74xxjuxPFeKH8giQkrxaAP0XNNZG5wuxZ/66nfX0hqu9cj5WFofra4uEr0sbc6xXyyDgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('47250539de3b4c9b5f35c0c62ed15527')

# 用來記錄每個用戶的狀態
user_states = {}

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text

    # 重置遊戲功能
    if text == "重新":
        user_states[user_id] = 'start'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="新的一局開始！\n\n你是一位探險家，進入了一座神秘的森林，面臨著未知的挑戰。你看到兩條小路，一條被藤蔓覆蓋，另一條光線充足。你選擇：\n\n1. 走進藤蔓覆蓋的小路\n2. 選擇光線充足的小路")
        )
        return

    if user_id not in user_states:
        # 新用戶，從頭開始
        user_states[user_id] = 'start'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你是一位探險家，進入了一座神秘的森林，面臨著未知的挑戰。你看到兩條小路，一條被藤蔓覆蓋，另一條光線充足。你選擇：\n\n1. 走進藤蔓覆蓋的小路\n2. 選擇光線充足的小路")
        )
    else:
        state = user_states[user_id]
        if state == 'start':
            if text == '1':
                user_states[user_id] = 'vine_path'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你踏入藤蔓小路，四周變得越來越黑暗。隱約間，你聽到低語聲，像是有人在訴說著故事。你選擇：\n\n1. 繼續前行\n2. 決定返回入口")
                )
            elif text == '2':
                user_states[user_id] = 'bright_path'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="光線充足的小路漸漸通向一片空地，你看到兩個出口。你選擇：\n\n1. 走向陰暗的洞穴\n2. 選擇明亮的出口")
                )
        elif state == 'vine_path':
            if text == '1':
                user_states[user_id] = 'treasure_room'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你來到了寶藏房間，但地板開始塌陷！你選擇：\n\n1. 跳向寶藏\n2. 立刻逃跑")
                )
            elif text == '2':
                user_states[user_id] = 'give_up'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你選擇返回入口，錯過了探索的機會。結局：安全的放棄。\n\n輸入 '重新' 開始新的一局！")
                )
        elif state == 'bright_path':
            if text == '1':
                user_states[user_id] = 'dark_cave'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你進入了陰暗的洞穴，四周靜得出奇，突然前方出現一隻巨大的怪物！你選擇：\n\n1. 戰鬥\n2. 逃跑")
                )
            elif text == '2':
                user_states[user_id] = 'bright_exit'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你選擇了平靜的田野，過上了簡單而快樂的生活。\n\n輸入 '重新' 開始新的一局！")
                )
        elif state == 'treasure_room':
            if text == '1':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你成功拿到了寶藏，但地板完全塌陷，你被困在裡面。結局：寶藏的囚徒。\n\n輸入 '重新' 開始新的一局！")
                )
            elif text == '2':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你選擇逃跑，成功離開了寶藏房間，但錯過了寶藏。結局：空手而歸。\n\n輸入 '重新' 開始新的一局！")
                )
        elif state == 'dark_cave':
            if text == '1':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你勇敢地面對怪物，但被打敗了。結局：英勇的犧牲。\n\n輸入 '重新' 開始新的一局！")
                )
            elif text == '2':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你成功逃脫，避免了死亡的威脅。結局：驚險逃生。\n\n輸入 '重新' 開始新的一局！")
                )


if __name__ == "__main__":
    # 指定端口為 8080
    app.run(debug=True, host="0.0.0.0", port=8080)