import datetime

# ngrok url 每次都要換
NGROK_URL = "https://healthy-helper.azurewebsites.net"
DRINK_DATABASE_NAME = "./databases/DB_drink.db"
WEIGHT_DATABASE_NAME = "./databases/DB_weight.db"
DINNER_DATABASE_NAME = "./databases/DB_dinner.db"
DATE, TIME = (str(datetime.datetime.now()).split())

COMMAND = """
🤖 指令 🤖
🔰 /體重 [小數(kg)]：輸入體重
🔰 /容量 [整數(ml)]：輸入水瓶容量
🔰 /晚餐：晚餐決定器 (隨機決定)
🔰 /晚餐 -列表：列出目前所有晚餐
🔰 /晚餐 -新增 [名稱 名稱 ...]
🔰 /晚餐 -移除 [名稱 名稱 ...]

🤖 語音命令 🤖
🔰 坐姿提醒
🔰 體重監控
🔰 喝水提醒
🔰 運動提醒
🔰 決定晚餐
"""
