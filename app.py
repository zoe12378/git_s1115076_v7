import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import LineBotApiError, InvalidSignatureError

app = Flask(__name__)

LINE_CHANNEL_SECRET = '47250539de3b4c9b5f35c0c62ed15527'
LINE_CHANNEL_ACCESS_TOKEN = '/ifIOXVIsQQPpwIukXv4QDZgA979eZSAC5G87k1JLKZnG0xSriHyC+xtydkAxVX0eKBXB/KyCdkMNx3oCm74xxjuxPFeKH8giQkrxaAP0XNNZG5wuxZ/66nfX0hqu9cj5WFofra4uEr0sbc6xXyyDgdB04t89/1O/w1cDnyilFU='

if not LINE_CHANNEL_SECRET or not LINE_CHANNEL_ACCESS_TOKEN:
    print("LINE_CHANNEL_SECRET 或 LINE_CHANNEL_ACCESS_TOKEN 未設置，請確認環境變數是否正確。")
    exit(1)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 載入故事檔案
with open('story.json', 'r', encoding='utf-8') as f:
    story = json.load(f)

# 用戶資料儲存（這邊可以用資料庫儲存）
user_data = {}

# 設置Webhook路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理用戶訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    
    if user_id not in user_data:
        # 初始化使用者資料
        user_data[user_id] = {
            "choices": [],
            "final_ending": None
        }
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=story['story']['intro'])
        )
    else:
        if user_data[user_id]['final_ending'] is None:
            # 根據使用者的選擇來確定當前步驟
            current_step = len(user_data[user_id]['choices']) + 1
            step = story['story']['steps'].get(str(current_step))
            
            if step:
                prompt = step['prompt']
                choices = step['choices']
                quick_reply_buttons = [
                    QuickReplyButton(action=MessageAction(label=label, text=str(choice)))
                    for choice, label in choices.items()
                ]
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=prompt,
                        quick_reply=QuickReply(items=quick_reply_buttons)
                    )
                )
            else:
                # 到達結局
                ending_key = "ending_" + str(user_data[user_id]['choices'][-1])
                user_data[user_id]['final_ending'] = ending_key
                ending_text = story['story']['endings'][ending_key]["text"]
                restart_text = story['story']['endings'][ending_key]["restart"]
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{ending_text}\n\n{restart_text}")
                )
        else:
            # 如果有最終結局，等待重新開始
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="遊戲結束了，若想重新開始，請回覆'重新開始'")
            )


# 處理使用者選擇的回應
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    choice = event.postback.data
    
    # 處理重新開始的情況
    if choice == '重新開始':
        user_data[user_id] = {
            "choices": [],
            "final_ending": None
        }
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=story['story']['intro'])
        )
    else:
        # 儲存用戶的選擇並繼續
        user_data[user_id]['choices'].append(choice)
        current_step = len(user_data[user_id]['choices']) + 1
        step = story['story']['steps'].get(str(current_step))
        
        if step:
            prompt = step['prompt']
            choices = step['choices']
            quick_reply_buttons = [
                QuickReplyButton(action=MessageAction(label=label, text=str(choice)))
                for choice, label in choices.items()
            ]
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=prompt,
                    quick_reply=QuickReply(items=quick_reply_buttons)
                )
            )
        else:
            # 若無選擇選項，直接進入結局
            ending_key = step.get("next_step", {}).get("default") or "ending_1"
            final_ending = story['story']['endings'].get(ending_key)
            
            if final_ending:
                user_data[user_id]['final_ending'] = ending_key
                ending_text = final_ending["text"]
                restart_text = final_ending["restart"]
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{ending_text}\n\n{restart_text}")
                )


if __name__ == "__main__":
    # 指定端口為 8080
    app.run(debug=True, host="0.0.0.0", port=8080)
