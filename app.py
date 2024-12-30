from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import json
import os

app = Flask(__name__)

# 替換為你自己的 LINE Messaging API token 和 channel secret
LINE_BOT_API_TOKEN = '/ifIOXVIsQQPpwIukXv4QDZgA979eZSAC5G87k1JLKZnG0xSriHyC+xtydkAxVX0eKBXB/KyCdkMNx3oCm74xxjuxPFeKH8giQkrxaAP0XNNZG5wuxZ/66nfX0hqu9cj5WFofra4uEr0sbc6xXyyDgdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '47250539de3b4c9b5f35c0c62ed15527'

line_bot_api = LineBotApi(LINE_BOT_API_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 讀取 JSON 檔案
with open('story.json', 'r', encoding='utf-8') as f:
    story_data = json.load(f)

# 儲存用戶進度
user_data = {}

@app.route("/callback", methods=['POST'])
def callback():
    # 取得 X-Line-Signature 標頭中的簽名值
    signature = request.headers['X-Line-Signature']

    # 取得請求正文
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # 處理請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_text = event.message.text.strip()

    if user_id not in user_data:
        # 初次互動，顯示引言並進入第一步
        user_data[user_id] = {
            'choices': [],
            'current_step': '1',
            'final_ending': None
        }
        send_story_step(user_id, '1')
    else:
        # 處理用戶的選擇
        current_step = user_data[user_id]['current_step']
        next_step = handle_choice(user_id, current_step, user_text)
        send_story_step(user_id, next_step)

def send_story_step(user_id, step_id):
    """根據當前步驟 ID 發送故事的 prompt 和選項。"""
    step_data = story_data['story']['steps'].get(step_id, None)
    if not step_data:
        return

    prompt = step_data['prompt']
    choices = step_data.get('choices', {})

    if choices:
        # 如果有選項，顯示 prompt 和選項
        choices_text = "\n".join([f"{key}. {value}" for key, value in choices.items()])
        line_bot_api.push_message(user_id, TextSendMessage(text=f"{prompt}\n\n{choices_text}"))
    else:
        # 沒有選項則進入結局
        ending_key = story_data['story']['steps'][step_id]['next_step']['default']
        send_ending(user_id, ending_key)

def handle_choice(user_id, current_step, user_text):
    """處理用戶選擇，返回下一步的 ID。"""
    step_data = story_data['story']['steps'].get(current_step, None)
    if not step_data or 'choices' not in step_data:
        return '1'  # 預設返回第一步

    user_choice = user_text.strip()

    if user_choice in step_data['choices']:
        # 儲存用戶選擇
        user_data[user_id]['choices'].append(user_choice)
        next_step = step_data['next_step'].get(user_choice, None)
        user_data[user_id]['current_step'] = next_step
        return next_step
    else:
        # 無效選擇，重新顯示選項
        return current_step

def send_ending(user_id, ending_key):
    """顯示結局。"""
    ending_text = story_data['story']['endings'].get(ending_key, "未知的結局")
    user_data[user_id]['final_ending'] = ending_key
    line_bot_api.push_message(user_id, TextSendMessage(text=ending_text))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
