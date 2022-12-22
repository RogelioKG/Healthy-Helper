# import flask related
from flask import Flask, request, abort, url_for
from urllib.parse import parse_qsl, parse_qs

# import line bot related
from linebot.models import events
from line_chatbot_api import *
from service_actions.service import *
from service_actions.posture import *

# import speech recognition
import speech_recognition as sr

# import others
import os
import random


# create flask server
app = Flask(__name__)
# ngrok link (每次都要換)
ngrok_url = "https://9bf7-140-115-204-45.ngrok.io"


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return "OK"


def transcribe(wav_path):
    """
    Speech to Text by Google free API
    language: en-US, zh-TW
    """
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        return r.recognize_google(audio, language="zh-TW")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as error:
        print(f"Could not request results from Google Speech Recognition service; {error}")


def deal_with_text(event, receive_text):
    messages = []

    if "坐姿提醒" in receive_text:
        messages.append(TextSendMessage(text="沒問題👍\n請上傳一張坐姿圖片\n我們會判斷這個人是否駝背"))
    elif "體重監控" in receive_text:
        messages.append(StickerSendMessage(package_id=446, sticker_id=2000))
        messages.append(TextSendMessage(text="功能還沒有做完請各位耐心等待RRRR~~~~"))
    elif "喝水提醒" in receive_text:
        messages.append(drink(event))
    elif "運動提醒" in receive_text:
        messages.append(exercise(event))
    else:
        messages.append(StickerSendMessage(package_id=789, sticker_id=10882))
        messages.append(TextSendMessage(text="抱歉我沒有聽懂，可以用其他方式再說一次嗎？"))

    return messages


@handler.add(PostbackEvent)
def handle_postback(event):
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    postback_data = dict(parse_qsl(event.postback.data))
    sticker_list=[(1070, 17840), (6362, 11087942), (11537, 52002734), (11539, 52114146)]
    sticker_random = random.choice(sticker_list)
    messages = []

    if postback_data.get("action") == "運動提醒":
        messages.append(StickerSendMessage(package_id=sticker_random[0], sticker_id=sticker_random[1]))
        messages.append(TextSendMessage(text=f"讚哦！來做點{postback_data.get('item')}吧！\n{postback_data.get('link')}"))

    line_bot_api.reply_message(event.reply_token, messages)


@handler.add(MessageEvent)
def handle_something(event):
    messages = []
    if event.message.type == "text":
        receive_text = event.message.text
        messages = deal_with_text(event, receive_text)
    elif event.message.type == "sticker":
        receive_sticker_id = event.message.sticker_id
        receive_package_id = event.message.package_id
        messages.append(StickerSendMessage(package_id=receive_package_id, sticker_id=receive_sticker_id))
    elif event.message.type == "image":
        image_content = line_bot_api.get_message_content(event.message.id)
        input_filename_jpg = "./static/posture_image/temp_image.jpg"
        with open(input_filename_jpg, "wb") as fd:
            for chunk in image_content.iter_content():
                fd.write(chunk)
        output_filename, ishunchback = detect_hunchback(input_filename_jpg)
        messages.append(ImageSendMessage(original_content_url = ngrok_url + output_filename[1:],
                                         preview_image_url = ngrok_url + output_filename[1:]))
        if ishunchback:
            messages.append(TextSendMessage(text="這是哪位？駝背好嚴重🤔"))
        else:
            messages.append(TextSendMessage(text="沒有駝背🤗"))
    elif event.message.type == "audio":
        filename_wav = "temp_audio.wav"
        filename_mp3 = "temp_audio.mp3"
        audio_content = line_bot_api.get_message_content(event.message.id)
        with open(filename_mp3, "wb") as fd:
            for chunk in audio_content.iter_content():
                fd.write(chunk)
        os.system(f"ffmpeg -y -i {filename_mp3} {filename_wav} -loglevel quiet")
        receive_text = transcribe(filename_wav)
        messages = deal_with_text(event, receive_text)

    line_bot_api.reply_message(event.reply_token, messages)

# run app
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5566, debug=True)