import sqlite3
import random
import uuid
from line_chatbot_api import *
from global_variables import *



####################### messages ######################


def drink(event, date: str = DATE):
    user_id = event.source.user_id
    new = False
    messages = []

    if exist_in_drink(user_id):
        if date != fetch_last_updated(user_id):
            update_drinked(user_id, reset=True)
        update_drinked(user_id)
        weight = fetch_weight_in_drink(user_id)
        drinked = fetch_drinked(user_id)
        expected = formula(weight)
        messages.append(TextSendMessage(text=f"達標飲水量：{expected}ml\n目前飲水量：{drinked}ml"))
        if drinked >= expected:
            messages.append(TextSendMessage(text="今天達標囉！"))
            messages.append(StickerSendMessage(package_id=8522, sticker_id=16581276))
        else:
            messages.append(TextSendMessage(text="加油加油！"))
    else:
        new = True
        messages.append(TextSendMessage(text="嗨嗨，你是第一次使用吧😊\n請輸入你的「體重」\n與水瓶的「容量」吧\n從今以後我和你的水瓶\n就是好朋友囉！"))
        messages.append(TextSendMessage(text="🤖 輸入指令 「/體重 55.4」\n將你的體重設為 55.4 kg\n🤖 輸入指令 「/容量 400」\n將你的水瓶容量設為 400 ml\n今後也可以任意調整"))
        messages.append(TextSendMessage(text="之後只要喝完一杯水\n再點擊「喝水提醒」\n健康小幫手就會自動幫你紀錄哦👍"))
        create_drink_user(user_id)

    return (messages, new)


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


def fetch_weight_in_drink(UserID: str) -> float:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    weight = cur.execute(f"SELECT weight FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0][0]
    con.close()
    return weight


def fetch_drinked(UserID: str) -> int:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    drinked = cur.execute(f"SELECT drinked FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0][0]
    con.close()
    return drinked


def fetch_last_updated(UserID: str) -> str:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    result = cur.execute(f"SELECT last_updated FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0][0]
    con.close()
    return result


######################## update ########################


def update_weight_in_drink(UserID: str, weight: float, *, date: str = DATE) -> None:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    cur.execute(f"UPDATE Info SET weight = {weight}, last_updated = \'{date}\' WHERE UserID = \'{UserID}\'")
    con.commit()
    con.close()


def update_drinked(UserID: str, *, date: str = DATE, reset: bool = False) -> None:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()

    if reset:
        drinked = 0
    else:
        drinked, cup = cur.execute(f"SELECT drinked, cup FROM Info WHERE UserID = \'{UserID}\'").fetchall()[0]
        drinked += cup

    cur.execute(f"UPDATE Info SET drinked = {drinked}, last_updated = \'{date}\' WHERE UserID = \'{UserID}\'")
    con.commit()
    con.close()


def update_cup(UserID: str, cup: int, *, date: str = DATE) -> None:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    cur.execute(f"UPDATE Info SET cup = {cup}, last_updated = \'{date}\' WHERE UserID = \'{UserID}\'")
    con.commit()
    con.close()


######################## others #######################


def create_drink_user(UserID: str, weight: float = 0, cup: int = 0, *, date: str = DATE) -> None:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    drinked = 0
    cur.execute(f"INSERT INTO Info (`UserID`, `weight`, `drinked`, `cup`, `last_updated`) VALUES (\'{UserID}\',{weight},{drinked},{cup},\'{date}\')")
    con.commit()
    con.close()


def exist_in_drink(UserID: str) -> bool:
    con = sqlite3.connect(DRINK_DATABASE_NAME)
    cur = con.cursor()
    result = cur.execute(f"SELECT EXISTS(SELECT 1 FROM Info WHERE UserID = \'{UserID}\')").fetchall()[0][0]
    con.close()
    return bool(result)


###################### debugging ######################


def test_data_for_drink(number: int) -> None:
    """
    @debugging
    """
    for _ in range(number):
        UserID = uuid.uuid1().hex
        weight = random.randint(50, 99)
        cup = random.randint(500, 999)
        create_drink_user(UserID, weight, cup)


######################### test ########################

if __name__ == "__main__":
    test_data_for_drink(10)
