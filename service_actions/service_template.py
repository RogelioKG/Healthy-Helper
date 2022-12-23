from line_chatbot_api import *

# ButtonsTemplate 保留選項模板
def call_service(event):
    message = TemplateSendMessage(
        alt_text="Buttons template",
        template=ButtonsTemplate(
            thumbnail_image_url="https://i.imgur.com/rfgMcFM.jpg",
            title="請問需要什麼服務呢?",
            text="請在下方點選您需要的服務項目",
            actions=[
                MessageAction(
                    label="坐姿提醒",
                    text="坐姿提醒"
                ),
                MessageAction(
                    label="體重監控",
                    text="體重監控"
                ),
                MessageAction(
                    label="喝水提醒",
                    text="喝水提醒"
                ),
                MessageAction(
                    label="運動提醒",
                    text="運動提醒"
                )
            ]
        )
    )
    return message
