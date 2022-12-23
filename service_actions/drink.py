import sqlite3
import random
import uuid
from line_chatbot_api import *
from variable import *

def drink(event):
    user_id = event.source.user_id
    messages = []

    if exist(user_id):
        if date != fetch_last_updated(user_id):
            update_drinked(user_id, reset=True)
        update_drinked(user_id)
        expected, drinked = fetch_expected_and_drinked(user_id)
        messages.append(TextSendMessage(text=f"達標飲水量：{expected}ml\n目前飲水量：{drinked}ml"))
        if drinked >= expected:
            messages.append(TextSendMessage(text="今天達標囉！"))
            messages.append(StickerSendMessage(package_id=8522, sticker_id=16581276))
        else:
            messages.append(TextSendMessage(text="加油加油！"))
    else:
        messages.append(TextSendMessage(text="嗨嗨，你是第一次使用吧😊\n請輸入你的「體重」\n與「水瓶」的容量吧\n從今以後我和你的水瓶\n就是好朋友囉！"))
        messages.append(TextSendMessage(text="🤖 輸入指令 「/體重 55.4」\n將你的體重設為 55.4 kg\n🤖 輸入指令 「/容量 400」\n將你的水瓶容量設為 400 ml\n今後也可以任意調整"))
        messages.append(TextSendMessage(text="之後只要喝完一杯水\n再點擊「喝水提醒」\n健康小幫手就會自動幫你紀錄哦👍"))
        create_user(user_id)

    return messages


####################### formula #######################


def formula(weight: float) -> int:
    """
    @param  weight: kg
    @return expected drinked water: ml
    喝水量公式：https://www.umsystem.edu/totalrewards/wellness/how-to-calculate-how-much-water-you-should-drink
    """
    kg_per_pounds = 0.45359237
    ml_per_oz = 29.5735296
    return int((weight / kg_per_pounds) * 0.5 * ml_per_oz)


######################## fetch ########################


def fetch_expected_and_drinked(UserID: str) -> tuple[int, int]:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    expected, drinked = cur.execute(f"SELECT expected, drinked FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0]
    con.close()
    return (expected, drinked)


def fetch_last_updated(UserID: str) -> str:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    result = cur.execute(f"SELECT last_updated FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0][0]
    con.close()
    return result


def fetch_last_updated(UserID: str) -> str:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    result = cur.execute(f"SELECT last_updated FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0][0]
    con.close()
    return result


######################## update ########################


def update_weight_and_expected(UserID: str, weight: float) -> None:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    expected = formula(weight)
    cur.execute(f"UPDATE Info SET expected = {expected}, last_updated = \'{date}\' WHERE UserID = \'{UserID}\'")
    con.commit()
    con.close()


def update_drinked(UserID: str, *, reset: bool = False) -> None:
    con = sqlite3.connect(database_name)
    cur = con.cursor()

    if reset:
        drinked = 0
    else:
        drinked, cup = cur.execute(f"SELECT drinked, cup FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0]
        drinked += cup

    cur.execute(f"UPDATE Info SET drinked = {drinked}, last_updated = \'{date}\' WHERE UserID = \'{UserID}\'")
    con.commit()
    con.close()


def update_cup(UserID: str, cup: int) -> None:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    cur.execute(f"UPDATE Info SET cup = {cup}, last_updated = \'{date}\' WHERE UserID = \'{UserID}\'")
    con.commit()
    con.close()


######################## others #######################

def exist(UserID: str) -> bool:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    result = cur.execute(f"SELECT EXISTS(SELECT 1 FROM Info WHERE UserID = \'{UserID}\')").fetchall()[0][0]
    con.close()
    return bool(result)


def create_user(UserID: str, weight: float = 0, cup: int = 0) -> None:
    con = sqlite3.connect(database_name)
    cur = con.cursor()
    expected = int(formula(weight))
    drinked = 0
    cur.execute(f"INSERT INTO Info (`UserID`, `expected`, `drinked`, `cup`, `last_updated`) VALUES (\'{UserID}\',{expected},{drinked},{cup},\'{date}\')")
    con.commit()
    con.close()


def test_data(number: int) -> None:
    """
    @debugging
    """
    for i in range(number):
        UserID = uuid.uuid1().hex
        weight = random.randint(50, 99)
        cup = random.randint(500, 999)
        create_user(UserID, weight, cup)
