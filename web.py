from flask import Flask
from google import genai
from google.genai import types # 1. 匯入 types 模組來設定進階參數


import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, make_response, jsonify

# 判斷是在 Vercel 還是本地
if os.path.exists('serviceAccountKey.json'):
    # 本地環境：讀取檔案
    cred = credentials.Certificate('serviceAccountKey.json')
else:
    # 雲端環境：從環境變數讀取 JSON 字串
    firebase_config = os.getenv('FIREBASE_CONFIG')
    cred_dict = json.loads(firebase_config)
    cred = credentials.Certificate(cred_dict)

firebase_admin.initialize_app(cred)


from datetime import datetime
import random
app = Flask(__name__)
# 建立 Client 時保持括號空白！
# SDK 會自動去抓你設定的 GEMINI_API_KEY 環境變數

client = genai.Client()
@app.route("/AI")
def AI():
    # 每次使用者拜訪該路徑時，直接使用全域的 client 呼叫模型
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents='我想查詢靜宜大學資管系的評價？',
    )
    
    # 回傳生成的文字
    return response.text


@app.route('/ask', methods=['GET', 'POST']) 
def ask():
    if request.method == "POST":
        user_prompt = request.form.get('prompt', '')
        if not user_prompt:
            return "請輸入內容", 400
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=user_prompt,
            )
            return response.text
        except Exception as e:
            return f"發生錯誤: {str(e)}", 500

    else:    
        # 當使用者直接打開網頁 (GET) 時，顯示輸入框畫面
        return render_template("ask.html")




@app.route("/")
def index():
    link = "<h1>歡迎進入黃義祥的網站首頁</h1>"
    link += "<a href=/mis>課程</a><hr>"
    link += "<a href=/today>今天日期</a><hr>"
    link += "<a href=/about>關於義祥</a><hr>"
    link += "<a href=/welcome?u=黃義&dep=靜宜資管>GET傳值</a><hr>"
    link += "<a href=/account>POST傳值(帳號密碼)</a><hr>"
    link += "<a href=/calc>數學運算</a><hr>"
    link += "<a href=/cup>擲茭</a><hr>"
    link += "<br><a href=/read>讀取Firestore資料(根據lab遞減，取前4)</a><br>"
    link += "<a href=/search>查詢老師姓名關鍵字</a><br>"
    link += "<a href=/movie>查詢開眼即將上映電影</a><br>"
    link += "<a href=/movie2>電影最近更新的日期</a><br>"
    link += "<a href=/movie3>查詢相關電影資訊</a><br>"
    link += "<a href=/road>道路事故查詢</a><br>"
    link += "<a href=/weather>查詢縣市天氣</a><br>"
    link += "<a href=/rate>本周新片DB(含電影分級) </a><br>"
    link += "<a href=/demo>查詢電影、笑話Agent</a><br>"
    link += "<a href=/AI>'我想查詢靜宜大學資管系的評價？'</a><br>"
    link += "<a href=/ask>詢問Gemini</a><br>"
    return link




@app.route("/demo")
def demoo():
    return render_template("demo.html")


# 初始化 Firestore 
db = firestore.client()

@app.route("/webhook", methods=["POST"])
def webhook():
    # 取得 Dialogflow 傳來的 JSON
    req = request.get_json(force=True)
    
    # 取得 action
    action = req["queryResult"]["action"]
    
    if (action == "rateChoice"):
        # 取得使用者選擇的分級
        rate = req["queryResult"]["parameters"]["rate"]
        
        # 查詢 Firestore 資料庫
        collection_ref = db.collection("本週新片含分級")
        docs = collection_ref.where("rate", "==", rate).get()
        
        # 標題資訊
        info = f"🎬 我是黃義祥設計的電影機器人\n"
        info += f"您選擇的分級：【{rate}】\n"
        
        movie_details = ""
        count = 0
        
        for doc in docs:
            count += 1
            movie_data = doc.to_dict()
            
            # 抓取電影標題
            title = movie_data.get("title", "未命名電影")
            
            # 🔥 關鍵修正：這裡必須對應你在 /rate 裡面寫的 "hyperlink"
            link = movie_data.get("hyperlink", "暫無連結資訊") 
            
            # 分段格式化：加入分隔線讓手機 LINE 更好閱讀
            movie_details += f"━━━━━━━━━━━━━━\n"
            movie_details += f"🎥 第 {count} 部：{title}\n"
            movie_details += f"🔗 介紹連結：\n{link}\n" # 網址換行顯示，方便點擊

        
        if count > 0:
            final_response = f"{info}本週共有 {count} 部相關影片：\n{movie_details}"
        else:
            final_response = f"{info}\n抱歉，本週新片中目前沒有【{rate}】分級的電影喔！"

        return make_response(jsonify({
            "fulfillmentText": final_response
        }))

    elif (action == "input.unknown"):

        # 2. 建立設定物件，設定你希望限制的最大 Token 數（例如 500）
        ai_config = types.GenerateContentConfig(
            max_output_tokens = 500
        )

        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents = req["queryResult"]["queryText"],
            config =ai_config,
        )
        info =  response.text
    

    return make_response(jsonify({"fulfillmentText": info}))

@app.route("/rate")
def rate():
    #本週新片
    url = "https://www.atmovies.com.tw/movie/new/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    lastUpdate = sp.find(class_="smaller09").text[5:]
    print(lastUpdate)
    print()

    result=sp.select(".filmList")

    for x in result:
        title = x.find("a").text
        introduce = x.find("p").text

        movie_id = x.find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw/movie/" + movie_id
        picture = "https://www.atmovies.com.tw/photo101/" + movie_id + "/pm_" + movie_id + ".jpg"

        r = x.find(class_="runtime").find("img")
        rate = ""
        if r != None:
            rr = r.get("src").replace("/images/cer_", "").replace(".gif", "")
            if rr == "G":
                rate = "普遍級"
            elif rr == "P":
                rate = "保護級"
            elif rr == "F2":
                rate = "輔12級"
            elif rr == "F5":
                rate = "輔15級"
            else:
                rate = "限制級"

        t = x.find(class_="runtime").text

        t1 = t.find("片長")
        t2 = t.find("分")
        showLength = t[t1+3:t2]

        t1 = t.find("上映日期")
        t2 = t.find("上映廳數")
        showDate = t[t1+5:t2-8]

        doc = {
            "title": title,
            "introduce": introduce,
            "picture": picture,
            "hyperlink": hyperlink,
            "showDate": showDate,
            "showLength": int(showLength),
            "rate": rate,
            "lastUpdate": lastUpdate
        }

        db = firestore.client()
        doc_ref = db.collection("本週新片含分級").document(movie_id)
        doc_ref.set(doc)
    return "本週新片已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate

@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        # 接收使用者輸入的縣市
        city = request.form["city"]
        
        # --- 以下為你提供的原始程式碼功能 ---
        city = city.replace("台","臺")
        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=rdec-key-123-45678-011121314&format=JSON&locationName="+ city
        Data = requests.get(url)
        
        # 解析資料
        jdata = json.loads(Data.text)
        WeatherTitle = jdata["records"]["datasetDescription"]
        Weather = jdata["records"]["location"][0]["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        Rain = jdata["records"]["location"][0]["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        # ----------------------------------

        # 將結果組合成網頁字串回傳
        res = f"<h3>{WeatherTitle}</h3>"
        res += f"{city}目前天氣預報<br>"
        res += f"{Weather}，降雨機率：{Rain}%"
        res += "<br><br><a href='/weather'>重新查詢</a> | <a href='/'>回到首頁</a>"
        return res
    else:
        # GET 請求時顯示輸入框
        html = """
        <form method="post">
            請輸入欲查詢的縣市：<input type="text" name="city" placeholder="例如：臺中市">
            <button type="submit">查詢</button>
        </form>
        <br><a href="/">回到首頁</a>
        """
        return html


@app.route("/movie3", methods=["GET", "POST"])
def movie3():
    if request.method == "POST":
        keyword = request.form["keyword"]
        db = firestore.client()
        # 指向你的電影資料庫集合
        collection_ref = db.collection("電影2A")
        docs = collection_ref.get()
        
        result = f"您查詢的電影關鍵字是：<b>{keyword}</b><br><br>"
        found = False
        
        for doc in docs:
            movie = doc.to_dict()
            # 判斷關鍵字是否在電影標題中 (忽略大小寫可用 .lower())
            if keyword in movie.get("title", ""):
                found = True
                result += f"電影名稱：{movie['title']}<br>"
                result += f"片長：{movie['showLength']} 分鐘<br>"
                result += f"上映日期：{movie['showDate']}<br>"
                result += f"最後更新：{movie.get('lastUpdate', '無資料')}<br>"
                result += f"介紹連結：{movie['hyperlink']} <a href='{movie['hyperlink']}' target='_blank'>點我觀看</a><br>"
                result += f"<img src='{movie['picture']}' width='200'><br><hr>"
        
        if not found:
            result += "抱歉，資料庫中找不到符合關鍵字的電影。"
            
        result += "<br><a href=/movie3>重新查詢</a>"
        result += "<br><a href=/>回到首頁</a>"
        return result
    else:
        # 這裡建議建立一個 search_movie.html，或暫時沿用 search.html 並修改其中的 action
        return render_template("search_movie.html")

@app.route("/road")
def road():
    R = ""
    url = " https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=a1b899c0-511f-4e3d-b22b-814982a97e41"
    Data = requests.get(url)
    #print(Data.text)

    JsonData = json.loads(Data.text)
    for item in JsonData:
        R += item["路口名稱"] + ",總共發生" + item["總件數"] + "件事故<br>"

    return R


@app.route("/movie2")
def movie2():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影2A").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 




# 新增的路由：爬取開演電影即將上映資訊
@app.route("/movie")
def movie():
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    
    R = "<h1>近期上映電影</h1>"
    for item in result:
        try:
            name = item.find("img").get('alt')
            link = "https://www.atmovies.com.tw" + item.find("a").get('href')
            R += f"電影名稱：{name}<br>"
            R += f"介紹連結：<a href='{link}' target='_blank'>{link}</a><br><br>"
        except:
            continue
    
    R += "<a href=/>回到首頁</a>"
    return R

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form["keyword"]
        db = firestore.client()
        collection_ref = db.collection("靜宜資管2026a")
        docs = collection_ref.get()
        
        result = f"您查詢的關鍵字是：{keyword}<br><br>"
        found = False
        for doc in docs:
            user = doc.to_dict()
            if keyword in user.get("name", ""):
                found = True
                result += f"{user['name']}老師的研究室是在{user['lab']}<br>"
        
        if not found:
            result += "抱歉，找不到符合關鍵字的老師。"
            
        result += "<br><a href=/search>重新查詢</a>"
        result += "<br><a href=/>回到首頁</a>"
        return result
    else:
        return render_template("search.html")

@app.route("/read")
def read():
    db = firestore.client()
    Temp = ""
    collection_ref = db.collection("靜宜資管2026a")
    docs = collection_ref.order_by("lab", direction=firestore.Query.DESCENDING).limit(4).get()

    for doc in docs:
        Temp += str(doc.to_dict()) + "<br>"

    return Temp

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1><a href=/>回到網站首頁<a>"

@app.route("/today")
def today():
    now = datetime.now()
    year = str(now.year)
    month = str(now.month)
    day = str(now.day)
    now = year +"年"+ month +"月"+day+"日"
    return render_template("today.html", datetime = now)

@app.route("/about")
def about():
   return render_template("mis2a.html")

@app.route("/welcome", methods=["GET"])
def welcome():
    x = request.values.get("u")
    y = request.values.get("dep")
    return render_template("welcome.html", name = x , dep = y )

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/calc", methods=["GET", "POST"])
def calc():
    if request.method == "POST":
        try:
            x = int(request.form["x"])
            y = int(request.form["y"])
        except ValueError:
            return render_template("calc.html", result="請輸入有效的整數！")

        opt = request.form["opt"]

        if opt == "/" and y == 0:
            result = "除數不能為0"
        else:
            match opt:
                case "+":
                    Result = x + y
                case "-":
                    Result = x - y
                case "*":
                    Result = x * y
                case "/":
                    Result = x / y
                case _:
                    return render_template("calc.html", result="無效的運算符號！")
            result = f"{x} {opt} {y} 的結果是 {Result}"

        return render_template("calc.html", result=result)
    else:
        return render_template("calc.html", result=None)

@app.route('/cup', methods=["GET"])
def cup():
    action = request.values.get("action")
    result = None
    
    if action == 'toss':
        x1 = random.randint(0, 1)
        x2 = random.randint(0, 1)
        
        if x1 != x2:
            msg = "聖筊：表示神明允許、同意，或行事會順利。"
        elif x1 == 0:
            msg = "笑筊：表示神明一笑、不解，或者考慮中，行事狀況不明。"
        else:
            msg = "陰筊：表示神明否定、憤怒，或者不宜行事。"
            
        result = {
            "cup1": "/static/" + str(x1) + ".jpg",
            "cup2": "/static/" + str(x2) + ".jpg",
            "message": msg
        }
        
    return render_template('cup.html', result=result)

@app.route("/sp1")
def sp1():
    R = ""
    url = "https://alan2026-a.vercel.app/about"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select("td a")

    for item in result:
        R += item.text + "<br>"+ item.get("href") + "<br><br>"
    return R

if __name__ == "__main__":
    app.run(debug=True)