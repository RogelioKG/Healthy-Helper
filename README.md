## **LINE Bot 程式運作**

> ### **`提醒`**
> 1. variable.py 裡的 NGROK_URL，每開一次 ngrok 要手動更改連結


> ### **`健康小幫手`**
>
> 1. [x] **坐姿提醒**
>    * 請上傳一張坐姿圖片
>        * 這是哪位？駝背好嚴重🤔
>        * 沒有駝背🤗
>
> 2. [x] **喝水提醒** `(使用 SQL)`
>    * 🔰 若使用者已開啟體重監控功能並記錄體重，會自動使用其體重資料
>    * 使用者點選(第一次)
>        * 輸入體重 -> 指令 "/體重 60.2" -> float
>        * 輸入容量 -> 指令 "/容量 400" -> int
>    * 使用者點選(之後)
>        * 目前飲水量自動以水杯容量加總
>        * 達標了會提醒
>    * database table: Info
>        * UserID 🔑 (Text)
>        * weight (Real)
>        * drinked (Integer)
>        * cup (Integer)
>        * last_updated (Text)
>
> 3. [x] **運動提醒**
>    * 護眼操 & 辦公室運動
>        * https://youtu.be/e6KfzPVTyRM
>        * https://youtu.be/umU1kLjvdkA
>        * https://youtu.be/KnyVWkU4I4M
>    * 居家冥想 & 伸展 & 肌肉訓練
>        * https://youtu.be/IqIo-5GNLmo
>        * https://youtu.be/g_tea8ZNk5A
>        * https://youtu.be/1f8yoFFdkcY
>
> 4. [x] **體重監控** `(使用 SQL + matplotlib)`
>    * 🔰 若使用者已開啟喝水提醒功能並記錄體重，會自動使用其體重資料
>    * 使用者點選(第一次)
>        * 輸入體重 -> 指令 "/體重 60.2" -> float
>    * 使用者點選(之後)
>        * 輸出該月體重紀錄圖表
>    * database table: Month
>        * UserID 🔑 (Text)
>        * timestamp (Text)
>        * day_1 (Real)
>        * ...
>        * day_31 (Real)
>
> 5. [x] **呼叫指令**
>    * 體重 {重量 (kg) }
>    * 容量 {水瓶體積 (ml) }
>
> 6. [ ] **獎勵系統**
>


> ### **`Function`**
>
> 1. **callback** \
>    處理在聊天室所發生的各種 Event
> 2. **transcribe** \
>    將音檔轉換成文字
> 3. **deal_with_text** \
>    解讀文字，並且回傳訊息模板
> 4. **deal_with_command** \
>    解讀指令 (以 slash '/' 開頭)，並且對資料庫進行操作
> 5. **handle_postback** \
>    負責處理使用者選擇後回傳的資訊 (PostbackEvent) \
>    (PostbackAction 的 data 即是回傳資訊，我們必需用 parse_qsl 將 & 拆開並轉成字典，分析應處理的動作)
>     * 運動提醒
> 6. **handle_something** \
>    負責處理使用者回傳的訊息 (MessageEvent) \
>    (MessageAction 的 text kw_arg 會自動幫使用者回傳訊息，這會再次觸發此函式)
>     * text \
>         處理文字所對應的服務 (由 deal_with_text 處理)
>     * sticker \
>         回傳相同的貼圖
>     * image \
>         怕圖片太大，所以每次切成一小塊寫入新的暫時圖片
>     * audio \
>         處理聲音所對應的服務 (由 transcribe 轉譯)


> ### **`Bugs or Doubts`**
> 1. **Doubts** 在判斷駝背的程式 hunchback.py 中，輸入非人類的圖片可能導致 Attributes Error
> - [x] Solved: 已解決，單純回復使用者無法處理
> 2. **Doubts** 在判斷駝背的程式 hunchback.py 中，resize 有可能導致判定失準
> - [x] Solved: 已解決，就按原大小就好，速度比較慢沒關係，圖片處理很正常的
> 3. **Doubts** 程式碼的架構在加上 weight.py 後變得很龐大 (或者是說我從來沒寫過這麼多行)
>               我很慶幸它是可以運作的，但我認為這會讓程式碼越來越難以維護
>               我認為我是使用很粗糙的方式在使用 database，這也可能導致程式運作變慢