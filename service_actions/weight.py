import sqlite3
import datetime
import random
import uuid
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from line_chatbot_api import *
from global_variables import *



####################### messages ######################


def weight(UserID, date: str = DATE):
    new = False
    messages = []

    if exist_in_weight(UserID):
        timestamp = fetch_timestamp(UserID)
        yt, mt, dt = map(int, timestamp.split("-"))
        y, m, d = map(int, date.split("-"))
        if not is_the_same_month(timestamp, date):
            img = draw_plot(UserID, date=(yt, mt, dt))
            messages.append(TextSendMessage(text=f"你好像還未在{m}月記錄體重\n但是我有你在{mt}月的體重紀錄"))
            messages.append(ImageSendMessage(original_content_url = NGROK_URL + img[1:],
                                                preview_image_url = NGROK_URL + img[1:]))
        else:
            img = draw_plot(UserID, date=(y, m, d))
            messages.append(TextSendMessage(text=f"🔰 {m}月的體重記錄 🔰"))
            messages.append(ImageSendMessage(original_content_url = NGROK_URL + img[1:],
                                             preview_image_url = NGROK_URL + img[1:]))
    else:
        new = True
        messages.append(TextSendMessage(text="嘿！歡迎你使用體重監控的功能😊\n每天輸入你的「體重」\n我可以幫你記錄成一張圖表哦"))
        messages.append(TextSendMessage(text="🤖 輸入指令 「/體重 55.4」\n將你今天的體重設為 55.4 kg\n今後也可以任意調整"))
        messages.append(TextSendMessage(text="之後只要點擊「體重監控」\n健康小幫手就會自動回傳\n你這個月的體重紀錄圖表哦👍"))
        create_weight_user(UserID)

    return (messages, new)


###################### matplotlib #####################


def draw_plot(UserID: str, *, date: tuple[int, int, int]):
    y, m, d = date
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (y % 4 == 0 and y % 100 != 0 or y % 400 == 0):
        days[2] += 1

    weights = [fetch_weight_in_weight(UserID, i) for i in range(1, 32)]
    y_list = [w for w in weights if w != 0]
    x_list = [i for i in range(1, days[m-1]+1) if weights[i-1] != 0]

    fig, ax = plt.subplots(1, 1, figsize=(16,9))
    ax.plot(x_list, y_list, marker=".")
    ax.set_xlabel("day")
    ax.set_ylabel("weight (kg)")
    ax.set_xlim(1, days[m-1])
    ax.grid(True)
    majorLocator = MultipleLocator(1)
    ax.xaxis.set_major_locator(majorLocator)

    img = "./static/weight_record/record.jpg"
    plt.savefig(img)

    return img


######################## fetch ########################


def fetch_timestamp(UserID: str) -> str:
    con = sqlite3.connect(WEIGHT_DATABASE_NAME)
    cur = con.cursor()
    result = cur.execute("SELECT timestamp FROM Month WHERE UserID = ?", (UserID,)).fetchall()[0][0]
    con.close()
    return result


def fetch_weight_in_weight(UserID: str, day: int) -> float:
    con = sqlite3.connect(WEIGHT_DATABASE_NAME)
    cur = con.cursor()
    result = cur.execute(f"SELECT day_{day} FROM Month WHERE UserID = ?", (UserID,)).fetchall()[0][0]
    con.close()
    return result


######################## update ########################


def update_weight_in_weight(UserID: str, weight: float, *, date: str = DATE) -> None:
    con = sqlite3.connect(WEIGHT_DATABASE_NAME)
    cur = con.cursor()
    day = int(date.split("-")[2])

    if not is_the_same_month(fetch_timestamp(UserID), date):
        for i in range(1, 32):
            cur.execute(f"UPDATE Month SET day_{i} = 0 WHERE UserID = ?", (UserID,))
    cur.execute(f"UPDATE Month SET day_{day} = ? WHERE UserID = ?", (weight, UserID))

    cur.execute("UPDATE Month SET timestamp = ? WHERE UserID = ?", (date, UserID))
    con.commit()
    con.close()


######################## others #######################


def create_weight_user(UserID: str, *, date: str = DATE) -> None:
    con = sqlite3.connect(WEIGHT_DATABASE_NAME)
    cur = con.cursor()
    cur.execute("INSERT INTO Month (`UserID`, `timestamp`) VALUES (?, ?)", (UserID, date))
    con.commit()
    con.close()


def exist_in_weight(UserID: str) -> bool:
    con = sqlite3.connect(WEIGHT_DATABASE_NAME)
    cur = con.cursor()
    result = cur.execute("SELECT EXISTS(SELECT 1 FROM Month WHERE UserID = ?)", (UserID,)).fetchall()[0][0]
    con.close()
    return bool(result)


def delete_weight_user(UserID: str) -> None:
    con = sqlite3.connect(WEIGHT_DATABASE_NAME)
    cur = con.cursor()
    cur.execute("DELETE FROM Month WHERE UserID = ?", (UserID,))
    con.commit()
    con.close()


def is_the_same_month(date1: str, date2: str) -> bool:
    return date1.split("-")[0:2] == date2.split("-")[0:2]


###################### debugging ######################


def test_date(y: int, m: int, d: int) -> str:
    return str(datetime.datetime(y, m, d)).split()[0]


def test_data_for_weight(number: int) -> None:
    """
    @debugging
    """
    for _ in range(number):
        UserID = uuid.uuid1().hex
        create_weight_user(UserID, date=test_date(2022, 10, 1))
        for i in range(1,20+1):
            weight = random.randint(60, 75)
            update_weight_in_weight(UserID, weight, date=test_date(2022, 10, i))


######################### test ########################

if __name__ == "__main__":
    test_data_for_weight(10)
