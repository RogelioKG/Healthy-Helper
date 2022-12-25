import sqlite3
import random
import uuid
from line_chatbot_api import *
from global_variables import *



####################### messages ######################


def decide_dinner(UserID: str) -> str:
    messages = []
    dinner_list = fetch_dinner_list(UserID)
    food_sticker_list = [(446, 1996), (446, 1997), (446, 1998), (789, 10865), (789, 10866), (789, 10863)]
    food_sticker = random.choice(food_sticker_list)
    if dinner_list:
        dinner = random.choice(dinner_list)
        messages.append(TextSendMessage(text=f"晚餐之神幫你決定的晚餐是：{dinner}！"))
        messages.append(StickerSendMessage(package_id=food_sticker[0], sticker_id=food_sticker[1]))
    else:
        messages.append(TextSendMessage(text=f"你還沒新增任何晚餐哦！\n趕緊新增一個吧！"))
        messages.append(StickerSendMessage(package_id=food_sticker[0], sticker_id=food_sticker[1]))
    return messages


######################## fetch ########################


def fetch_dinner_list(UserID: str) -> list[str]:
    con = sqlite3.connect(DINNER_DATABASE_NAME)
    cur = con.cursor()
    string: str = cur.execute(f"SELECT dinner FROM Decide WHERE UserID = ?", (UserID,)).fetchall()[0][0]
    dinner_list = string.split() if string is not None else []
    con.close()
    return dinner_list


######################## update ########################


def append_dinner(UserID: str, dinner: str) -> set[str]:
    """
    @return those dinner that has not existed in database.
    """
    dinner_set = set(dinner.split())
    dinner_set.difference_update(set(fetch_dinner_list(UserID)))
    size = len(dinner_set)
    dinner = " " + " ".join(dinner_set)

    con = sqlite3.connect(DINNER_DATABASE_NAME)
    cur = con.cursor()
    cur.execute("UPDATE Decide SET size = size + ?, dinner = dinner || ? WHERE UserID = ?", (size, dinner, UserID))
    con.commit()
    con.close()

    return dinner_set


def remove_dinner(UserID: str, dinner: str) -> None:
    dinner_set = set(fetch_dinner_list(UserID)) - set(dinner.split())
    size = len(dinner_set)
    dinner = " " + " ".join(dinner_set)

    con = sqlite3.connect(DINNER_DATABASE_NAME)
    cur = con.cursor()
    cur.execute("UPDATE Decide SET size = ?, dinner = ? WHERE UserID = ?", (size, dinner, UserID))
    con.commit()
    con.close()


######################## others #######################


def create_dinner_user(UserID: str) -> None:
    con = sqlite3.connect(DINNER_DATABASE_NAME)
    cur = con.cursor()
    cur.execute("INSERT INTO Decide (`UserID`) VALUES (?)", (UserID,))
    con.commit()
    con.close()


def exist_in_dinner(UserID: str) -> bool:
    con = sqlite3.connect(DINNER_DATABASE_NAME)
    cur = con.cursor()
    result = cur.execute("SELECT EXISTS(SELECT 1 FROM Decide WHERE UserID = ?)", (UserID,)).fetchall()[0][0]
    con.close()
    return bool(result)


def delete_dinner_user(UserID: str) -> None:
    con = sqlite3.connect(DINNER_DATABASE_NAME)
    cur = con.cursor()
    cur.execute("DELETE FROM Decide WHERE UserID = ?", (UserID,))
    con.commit()
    con.close()


###################### debugging ######################


def test_data(number: int) -> None:
    for _ in range(number):
        create_dinner_user(uuid.uuid1().hex)


######################### test ########################

if __name__ == "__main__":
    test_data(10)