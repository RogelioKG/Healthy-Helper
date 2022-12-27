# import flask related
from flask import Flask, request, abort, url_for
from urllib.parse import parse_qsl, parse_qs


# import line bot related
from linebot.models import events
from line_chatbot_api import *

# import service actions
from service_actions.exercise import *
from service_actions.posture import *
from service_actions.drink import *
from service_actions.weight import *
from service_actions.dinner import *

# import speech recognition
import speech_recognition as sr

# import standard library
import os
import random

# import others
from global_variables import *



# create flask server
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, Flask!'

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


@handler.add(MessageEvent)
def handle_message(event):
    messages = []

    if event.message.type == "text":
        receive_text = event.message.text
        if receive_text[0] == '/':
            messages = deal_with_command(event, receive_text)
        else:
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
        try:
            output_filename, ishunchback = detect_hunchback(input_filename_jpg)
            messages.append(ImageSendMessage(original_content_url = NGROK_URL + output_filename[1:],
                                             preview_image_url = NGROK_URL + output_filename[1:]))
            if ishunchback:
                messages.append(TextSendMessage(text="這是哪位？駝背好嚴重🤔"))
            else:
                messages.append(TextSendMessage(text="沒有駝背🤗"))
        except AttributeError:
            messages.append(TextSendMessage(text="不行，我看不出來😵‍💫"))
    elif event.message.type == "audio":
        filename_wav = "./static/audio/temp_audio.wav"
        filename_mp3 = "./static/audio/temp_audio.mp3"
        audio_content = line_bot_api.get_message_content(event.message.id)
        with open(filename_mp3, "wb") as fd:
            for chunk in audio_content.iter_content():
                fd.write(chunk)
        os.system(f"ffmpeg -y -i {filename_mp3} {filename_wav} -loglevel quiet")
        receive_text = transcribe(filename_wav)
        messages = deal_with_text(event, receive_text)

    line_bot_api.reply_message(event.reply_token, messages)


@handler.add(PostbackEvent)
def handle_postback(event):
    UserID = event.source.user_id
    user_name = line_bot_api.get_profile(UserID).display_name
    postback_data = dict(parse_qsl(event.postback.data))
    sticker_list=[(1070, 17840), (6362, 11087942), (11537, 52002734), (11539, 52114146)]
    sticker_random = random.choice(sticker_list)
    messages = []

    if postback_data.get("action") == "運動提醒":
        messages.append(StickerSendMessage(package_id=sticker_random[0], sticker_id=sticker_random[1]))
        messages.append(TextSendMessage(text=f"讚哦！來做點{postback_data.get('item')}吧！\n{postback_data.get('link')}"))

    line_bot_api.reply_message(event.reply_token, messages)


@handler.add(FollowEvent)
def handle_follow(event):
    UserID = event.source.user_id
    create_dinner_user(UserID)


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    UserID = event.source.user_id
    delete_drink_user(UserID)
    delete_weight_user(UserID)
    delete_dinner_user(UserID)



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


def deal_with_text(event, receive_text: str):
    UserID = event.source.user_id
    messages = []

    if "坐姿提醒" in receive_text:
        messages.append(TextSendMessage(text="沒問題👍\n請上傳一張坐姿圖片\n我們會判斷這個人是否駝背"))
    elif "體重監控" in receive_text:
        msg, new = weight(UserID)
        messages.extend(msg)
        if new and exist_in_drink(UserID):
            w = fetch_weight_in_drink(UserID)
            if w != 0:
                update_weight_in_weight(UserID, w)
                messages.append(TextSendMessage(text=f"你在「喝水提醒」中\n有紀錄今天的體重 {w} kg\n已經幫你填入「體重監控」囉！"))
    elif "喝水提醒" in receive_text:
        msg, new = drink(UserID)
        messages.extend(msg)
        if new and exist_in_weight(UserID):
            w = fetch_weight_in_weight(UserID, int(DATE.split("-")[2]))
            if w != 0:
                update_weight_in_drink(UserID, w)
                messages.append(TextSendMessage(text=f"你在「體重監控」中\n有紀錄今天的體重 {w} kg\n已經幫你填入「喝水提醒」囉！"))
    elif "運動提醒" in receive_text:
        messages.extend(exercise())
    elif "決定晚餐" in receive_text:
        messages.extend(decide_dinner(UserID))
    else:
        messages.append(StickerSendMessage(package_id=789, sticker_id=10882))
        messages.append(TextSendMessage(text="抱歉我沒有聽懂\n可以用其他方式再說一次嗎？"))

    return messages


def deal_with_command(event, receive_text: str):
    UserID = event.source.user_id
    messages = []

    if receive_text.startswith("/指令"):
        messages.append(TextSendMessage(text=COMMAND))
    elif receive_text.startswith("/體重"):
        has_drink_id = exist_in_drink(UserID)
        has_weight_id = exist_in_weight(UserID)
        try:
            if has_drink_id and not has_weight_id:
                weight = float(receive_text.split()[1])
                if weight <= 0:
                    messages.append(TextSendMessage(text=f"❌ 你是外星人嗎？體重 {weight} kg🤔"))
                else:
                    update_weight_in_drink(UserID, weight)
                    messages.append(TextSendMessage(text=f"✅ 體重更新完成\n你的每日需飲水量為 {formula(weight)} ml"))
            elif not has_drink_id and has_weight_id:
                weight = float(receive_text.split()[1])
                if weight <= 0:
                    messages.append(TextSendMessage(text=f"❌ 你是外星人嗎？體重 {weight} kg🤔"))
                else:
                    update_weight_in_weight(UserID, weight)
                    messages.append(TextSendMessage(text=f"✅ 體重更新完成\n你今天的體重為 {weight} kg"))
            elif has_drink_id and has_weight_id:
                weight = float(receive_text.split()[1])
                if weight <= 0:
                    messages.append(TextSendMessage(text=f"❌ 你是外星人嗎？體重 {weight} kg🤔"))
                else:
                    update_weight_in_drink(UserID, weight)
                    update_weight_in_weight(UserID, weight)
                    messages.append(TextSendMessage(text=f"✅ 體重更新完成\n你今天的體重為 {weight} kg\n你的每日需飲水量為 {formula(weight)} ml"))
            else:
                messages.append(TextSendMessage(text=f"請先點選「喝水提醒」\n或「體重監控」\n才能開啟此功能哦"))
        except ValueError:
            messages.append(TextSendMessage(text=f"❌ 嘿！你輸入的是數字嗎？🤔"))
        except IndexError:
            messages.append(TextSendMessage(text=f"🔰 /體重 [小數(kg)]：輸入體重"))
    elif receive_text.startswith("/容量"):
        try:
            if not exist_in_drink(UserID):
                raise KeyError
            cup = int(receive_text.split()[1])
            if cup <= 0:
                messages.append(TextSendMessage(text=f"❌ 哪個異世界的水瓶是 {cup} ml🤔"))
            else:
                update_cup(UserID, cup)
                messages.append(TextSendMessage(text=f"✅ 容量更新完成\n你的水瓶容量為 {cup} ml"))
        except ValueError:
            messages.append(TextSendMessage(text=f"❌ 嘿！你輸入的是整數嗎🤔"))
        except IndexError:
            messages.append(TextSendMessage(text=f"🔰 /容量 [整數(kg)]：輸入水瓶容量"))
        except KeyError:
            messages.append(TextSendMessage(text=f"請先點選「喝水提醒」\n才能開啟此功能哦"))
    elif receive_text.startswith("/晚餐"):
        receive_text = receive_text.removeprefix("/晚餐").strip()
        if receive_text.startswith("-列表"):
            string_list = ["你目前的晚餐列表："]
            for i, dinner in enumerate(fetch_dinner_list(UserID), start=1):
                string_list.append(f"🍽️ {i}. {dinner}")
            messages.append(TextSendMessage(text="\n".join(string_list)))
        elif receive_text.startswith("-新增"):
            receive_text = receive_text.removeprefix("-新增").strip()
            string_list = ["新增的晚餐："]
            dinner_set = append_dinner(UserID, receive_text)
            for dinner in dinner_set:
                string_list.append(f"🍽️ {dinner}")
            messages.append(TextSendMessage(text="\n".join(string_list)))
        elif receive_text.startswith("-移除"):
            receive_text = receive_text.removeprefix("-移除").strip()
            remove_dinner(UserID, receive_text)
            messages.append(TextSendMessage(text=f"移除完成！"))
        elif receive_text.startswith("-"):
            messages.append(TextSendMessage(text="嗯？我沒有這個指令欸\n如果忘記的話可以輸入「/指令」\n來查看可以使用哪些指令哦！"))
        else:
            messages.extend(decide_dinner(UserID))
    elif receive_text.startswith("/"):
        messages.append(StickerSendMessage(package_id=789, sticker_id=10882))
        messages.append(TextSendMessage(text="嗯？我沒有這個指令欸\n如果忘記的話可以輸入「/指令」\n來查看可以使用哪些指令哦！"))

    return messages


####################### run app #######################

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5566)
