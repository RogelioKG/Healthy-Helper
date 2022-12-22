## **LINE Bot 程式運作**


> ### **`健康小幫手`**
>
> 1. [x] **坐姿提醒**
>    * 請上傳一張坐姿圖片
>       * 這是哪位？駝背好嚴重🤔
>       * 沒有駝背🤗
> 2. [ ] **喝水提醒**
>    * (預計使用 SQL) 馬的，給我喝水喔
> 3. [x] **運動提醒**
>    * 護眼操 & 辦公室運動
>        * https://youtu.be/e6KfzPVTyRM
>        * https://youtu.be/umU1kLjvdkA
>        * https://youtu.be/KnyVWkU4I4M
>    * 居家冥想 & 伸展 & 肌肉訓練
>        * https://youtu.be/IqIo-5GNLmo
>        * https://youtu.be/g_tea8ZNk5A
>        * https://youtu.be/1f8yoFFdkcY
> 4. [ ] **體重監控**
>    * (預計使用 SQL + matplotlib)
> 5. [ ] **呼叫指令**
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
> 4. **handle_postback** \
>    負責處理使用者選擇後回傳的資訊 (PostbackEvent) \
>    (PostbackAction 的 data 即是回傳資訊，我們必需用 parse_qsl 將 & 拆開並轉成字典，分析應處理的動作)
>     * 運動提醒
> 5. **handle_something** \
>    負責處理使用者回傳的訊息 (MessageEvent) \
>    (MessageAction 的 text kw_arg 會自動幫使用者回傳訊息，這會再次觸發此函式)
>     * text \
>         處理文字所對應的服務 (由 deal_with_text 處理)
>     * sticker \
>         回傳相同的貼圖
>     * image \
>         怕圖片太大，所以每次切成一小塊寫入新的暫時圖片，
>     * audio \
>         處理聲音所對應的服務 (由 transcribe 轉譯)


> ### **`Bugs or Doubts`**
> 1. **Doubts** 在判斷駝背的程式 hunchback.py 中，輸入非人類的圖片可能導致 Attributes Error
> - [ ] 目前沒有對這個疑慮做出處置，因為它不會導致程式出錯
> 2. **Doubts** 在判斷駝背的程式 hunchback.py 中，resize 有可能導致判定失準
> - [ ] 目前沒有對這個疑慮做出處置