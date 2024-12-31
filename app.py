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
            TextSendMessage(text="新的一局開始！\n\n你是一位探險家，進入了一座神秘的森林，面臨著未知的挑戰\n據說森林的深處藏著一個無價的寶藏，但也隱藏著致命的危險\n你的每一個選擇都將改變你的命運，最終決定你是成為傳奇，還是空手而回\n你走進森林深處，面前出現了兩條截然不同的小路\n一條被茂密的藤蔓覆蓋，顯得幽深而神秘；另一條光線充足，看起來似乎較為安全\n\n選項1：走進藤蔓覆蓋的小路\n選項2：選擇光線充足的小路\n請輸入1 or 2來代表您的選擇")
        )
        return

    if user_id not in user_states:
        # 新用戶，從頭開始
        user_states[user_id] = 'start'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你是一位探險家，進入了一座神秘的森林，面臨著未知的挑戰\n據說森林的深處藏著一個無價的寶藏，但也隱藏著致命的危險\n你的每一個選擇都將改變你的命運，最終決定你是成為傳奇，還是空手而回\n你走進森林深處，面前出現了兩條截然不同的小路\n一條被茂密的藤蔓覆蓋，顯得幽深而神秘；另一條光線充足，看起來似乎較為安全\n\n選項1：走進藤蔓覆蓋的小路\n選項2：選擇光線充足的小路\n請輸入1 or 2來代表您的選擇")
        )
    else:
        state = user_states[user_id]
        if state == 'start':
            if text == '1':
                user_states[user_id] = 'vine_path'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你踏入藤蔓小路，四周變得越來越黑暗。隱約間，你聽到耳邊傳來低語聲，像是有人在訴說著不可思議的故事。地面上還出現了奇怪的腳印\n\n選項1：繼續前行，探索這條神秘的小路\n選項2：感到不安，決定返回入口\n請輸入1 or 2來代表您的選擇")
                )
            elif text == '2':
                user_states[user_id] = 'bright_path'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="光線充足的小路讓你感到安心，但漸漸地，你發現自己來到了一片空曠的草地。草地的盡頭有兩個出口，一個是陰暗的洞穴，另一個則是通向遠處明亮的出口\n\n選項1：走向陰暗的洞穴，感到這裡可能藏著什麼秘密\n選項2：選擇明亮的出口，期待光明的未來\n請輸入1 or 2來代表您的選擇")
                )
        elif state == 'vine_path':
            if text == '1':
                user_states[user_id] = 'treasure_room'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你進入了一個巨大的房間，房間中央擺滿了金光閃閃的寶藏。然而，當你踏進去時，地板開始發出刺耳的聲音，似乎隨時會崩塌\n\n選項1：冒險跳向寶藏，試圖帶走這些財富\n選項2：立刻逃跑，保住自己的性命\n請輸入1 or 2來代表您的選擇")
                )
            elif text == '2':
                user_states[user_id] = 'give_up'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你迅速返回了入口，深吸了一口氣，雖然安全了，但失去了探索的機會。你站在原地，對自己是否應該再次踏入森林感到猶豫\n結局：\n你選擇了安全地返回入口，避免了任何危險。然而，內心深處你始終感到遺憾，懷疑如果當初勇敢一些，是否能發現更大的世界\n輸入【重新】開始新的一局！")
                )
        elif state == 'bright_path':
            if text == '1':
                user_states[user_id] = 'dark_cave'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你進入了一個巨大的房間，房間中央擺滿了金光閃閃的寶藏。然而，當你踏進去時，地板開始發出刺耳的聲音，似乎隨時會崩塌\n\n選項1：冒險跳向寶藏，試圖帶走這些財富\n選項2：立刻逃跑，保住自己的性命\n請輸入1 or 2來代表您的選擇")
                )
            elif text == '2':
                user_states[user_id] = 'bright_exit'
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="明亮的出口通向一片廣闊的田野，這裡鮮花盛開，鳥兒鳴叫，一切都顯得那麼平靜。你感受到前所未有的舒適和自由，彷彿找到了心靈的歸宿\n結局：\n你選擇了通往田野的道路，過上了簡單而快樂的生活。或許你沒有獲得寶藏，但內心的平靜讓你無比滿足\n輸入 '重新' 開始新的一局！")
                )
        elif state == 'treasure_room':
            if text == '1':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你冒險跳向寶藏，雖然受了些輕傷，但你成功帶回了無價之寶，成為了傳奇的冒險家。這次探險的故事被世人傳頌，你的一生充滿了榮耀和冒險\n輸入 '重新' 開始新的一局！")
                )
            elif text == '2':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你果斷地選擇逃跑，雖然失去了寶藏，但你保住了自己的性命。或許這次的遺憾將激勵你在未來的探險中更加謹慎\n輸入 '重新' 開始新的一局！")
                )
        elif state == 'dark_cave':
            if text == '1':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你冒險跳向寶藏，雖然受了些輕傷，但你成功帶回了無價之寶，成為了傳奇的冒險家。這次探險的故事被世人傳頌，你的一生充滿了榮耀和冒險\n輸入 '重新' 開始新的一局！")
                )
            elif text == '2':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你果斷地選擇逃跑，雖然失去了寶藏，但你保住了自己的性命。或許這次的遺憾將激勵你在未來的探險中更加謹慎\n輸入 '重新' 開始新的一局！")
                )


if __name__ == "__main__":
    # 指定端口為 8080
    app.run(debug=True, host="0.0.0.0", port=8080)