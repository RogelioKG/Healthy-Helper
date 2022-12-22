from urllib.parse import parse_qsl, parse_qs
import datetime
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


def drink(event):
    message = TextSendMessage(text="馬的，給我喝水喔")
    return message

def exercise(event):
    message = TemplateSendMessage(
        alt_text="運動提醒",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://www.muscleandfitness.com/wp-content/uploads/2022/10/Office-workers-performing-anti-sitting-exercises-and-workout-at-their-desks.jpg?quality=86&strip=all",
                    title="護眼操與辦公室運動",
                    text="上班好累，放鬆一下吧！",
                    actions=[
                        PostbackAction(
                            label="舒緩肩頸痠痛",
                            display_text="想要舒緩肩頸痠痛😌",
                            data="action=運動提醒&item=舒緩肩頸痠痛&link=https://youtu.be/e6KfzPVTyRM"
                        ),
                        PostbackAction(
                            label="護眼操",
                            display_text="想要做個護眼操😌",
                            data="action=運動提醒&item=護眼操&link=https://youtu.be/umU1kLjvdkA"
                        ),
                        PostbackAction(
                            label="椅子瑜珈",
                            display_text="想要做椅子瑜珈😌",
                            data="action=運動提醒&item=椅子瑜珈&link=https://youtu.be/KnyVWkU4I4M"
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://www.helpguide.org/wp-content/uploads/woman-at-edge-of-dock-lotus-position.jpg",
                    title="居家冥想、伸展與肌肉訓練",
                    text="宅在家太久嗎？做點伸展吧！",
                    actions=[
                        PostbackAction(
                            label="居家輕伸展",
                            display_text="想要做個居家輕伸展😌",
                            data="action=運動提醒&item=居家輕伸展&link=https://youtu.be/IqIo-5GNLmo"
                        ),
                        PostbackAction(
                            label="Full Body Stretch",
                            display_text="想要做個全身伸展😌",
                            data="action=運動提醒&item=全身伸展&link=https://youtu.be/g_tea8ZNk5A"
                        ),
                        PostbackAction(
                            label="AB workout",
                            display_text="想要試試AB workout😌",
                            data="action=運動提醒&item=AB workout&link=https://youtu.be/1f8yoFFdkcY"
                        )
                    ]
                )
            ]
        )
    )
    return message
