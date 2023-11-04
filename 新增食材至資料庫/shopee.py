'''
input: 輸入食材種類 or 食材名稱(名稱需要出現在下面list內)

-1 => 更新全部種類食材
'''


from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import urllib
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import jieba

'''
食材分類
'''
vegetable_list = ["杏鮑菇", "金針菇", "香菇", "地瓜葉", "小白菜", "高麗菜", "青江菜", "菠菜", "油菜", "娃娃菜", "大陸妹", "花椰菜", "莧菜", "牛蒡", "洋蔥",
                  "紅蘿蔔", "馬鈴薯", "玉米筍", "白蘿蔔", "番茄", "秀珍菇", "木耳", "小黃瓜", "大黃瓜", "櫛瓜", "辣椒", "青椒", "甜椒", "玉米", "南瓜", "芹菜", "泡菜", "海帶"]
fruit_list = ["鳳梨", "蘋果", "香蕉", "檸檬"]
seasoning_list = ["九層塔", "薑", "黑胡椒", "醬油", "白糖", "紅糖", "醋", "糯米醋", "橄欖油", "味噌", "番茄醬", "蔥", "蔥花", "沙拉油", "麻油", "冰糖", "豆瓣醬",
                  "奶油", "白醋", "鹽", "五香粉", "美乃滋", "烏醋", "味醂", "香油", "白胡椒粉", "沙拉醬", "凱薩醬", "紅椒粉", "芥末醬", "魚露", "香茅", "花椒", "蜂蜜", "黑麻油"]
meat_list = ["牛肉", "豬肉", "羊肉", "雞肉", "肉片", "半雞", "全雞", "豬絞肉", "肉絲", "雞腿",
             "雞胸", "雞翅", "牛肉塊", "豬肉塊", "雞肉塊", "肉醬", "牛絞肉", "培根", "五花肉片", "牛五花肉", "豬五花肉"]
seafood_list = ["蝦仁", "蝦子", "小卷", "章魚", "透抽", "草蝦", "白蝦", "吳郭魚", "白鯧魚", "秋刀魚", "鮪魚", "鮭魚", "柳葉魚", "旗魚", "虱目魚",
                "沙丁魚", "黃魚", "鯖魚", "吻仔魚", "螃蟹", "蟹肉", "干貝", "花枝", "小管", "魚卵", "帆立貝", "螺肉", "蜆", "海瓜子", "比目魚", "海膽", "魷魚", "蛤"]
others = ["樹薯粉", "地瓜粉", "太白粉", "豆腐", "雞蛋", "肉鬆", "起司", "糯米粉", "玉米粉", "抹茶粉", "可可粉",
          "杏仁片", "牛奶", "泡打粉", "巧克力", "杏仁", "杏仁粉", "月桂葉", "咖哩", "綠咖哩", "中筋麵粉", "低筋麵粉", "蒜頭", "麵粉"]
grains_list = ["米", "烏龍麵", "米粉", "冬粉", "義大利麵", "筆管麵", "吐司", "麵包", "漢堡麵包"]

black_list = ["五桔國際", "快樂大廚義式醬汁"]


def categories(keyword: str) -> str:
    for i in range(len(vegetable_list)):
        if keyword == vegetable_list[i]:
            return "蔬菜"
    for i in range(len(fruit_list)):
        if keyword == fruit_list[i]:
            return "水果"
    for i in range(len(seasoning_list)):
        if keyword == seasoning_list[i]:
            return "調味料"
    for i in range(len(meat_list)):
        if keyword == meat_list[i]:
            return "肉類"
    for i in range(len(seafood_list)):
        if keyword == seafood_list[i]:
            return "海鮮"
    for i in range(len(others)):
        if keyword == others[i]:
            return "其他"
    for i in range(len(grains_list)):
        if keyword == grains_list[i]:
            return "主食"


# def item(key: str) -> list:
#    ls = []
#    tags = soup.select(key)
#   for i in tags:
#       ls.append(i.text)
#    return ls


def jiebaFilter(product: str, key: str) -> bool:
    for ch in ['(', ')', ' ', '【', '】', '/', '、', '\u3000', '／', '-', '*', '＊', '~', ]:
        if ch in product:
            product = product.replace(ch, '')
    text = [product]
    jieba.load_userdict('addDict.txt')

    f = open('delDict.txt', 'r', encoding='utf-8')
    for line in f.readlines():
        line = line.replace('\n', '')
        jieba.del_word(line)
    f.close()

    for sentence in text:
        seg_list = jieba.lcut(sentence, cut_all=False)
    for i in range(len(seg_list)):
        if seg_list[i] == key:
            print(seg_list, "True")
            return True
    #print(seg_list, "False")
    return False


cred = credentials.Certificate(
    r"test-4fa88-firebase-adminsdk-54nig-c645ede062.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


chrome_options = Options()
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
while True:
    keyword = input("請輸入關鍵字:")
    if(keyword == "蔬菜"):
        search = vegetable_list
    elif(keyword == "水果"):
        search = fruit_list
    elif(keyword =="調味料"):
        search = seasoning_list
    elif(keyword == "肉類"):
        search = meat_list
    elif(keyword =="海鮮"):
        search = seafood_list
    elif(keyword =="其他"):
        search = others
    elif(keyword  =="主食"):
        search = grains_list
    elif(keyword =="-1"):
        search = vegetable_list + fruit_list + seasoning_list + meat_list + seafood_list + others + grains_list
    else:
        search = [keyword]

    for z in range(len(search)):

        keyword = search[z]
        category = categories(search[z])
        print(keyword)
        print(category)
        key = keyword + " " + category

        # try:

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36 Edg/88.0.705.68',
            'x-api-source': 'pc',
            'referer': f'https://shopee.tw/search?keyword={urllib.parse.quote(key)}'
        }

        s = requests.Session()
        url = 'https://shopee.tw/api/v4/search/product_labels'
        r = s.get(url, headers=headers)

        base_url = 'https://shopee.tw/api/v2/search_items/'

        query = f"by=relevancy&keyword={key}&limit=50&newest=0&order=desc&page_type=search&version=2"
        url = base_url + '?' + query
        r = s.get(url, headers=headers)
        if r.status_code == requests.codes.ok:
            data = r.json()
            # print(data)

        ls = []
        # print(len(data['items']))  #50 items in one page
        name = ''
        link = ''
        
        for i in range(len(data['items'])):
            if (jiebaFilter(data['items'][i]['name'], keyword) == True):
                name = data['items'][i]['name']
                price_max = data['items'][i]['price_max']/100000
                price_min = data['items'][i]['price_min']/100000
                price = (price_max+price_min)/2
                itemid = data['items'][i]['itemid']
                shopid = data['items'][i]['shopid']
                # 網址bad request處理
                for ch in ['/', '%', '#']:
                    if ch in name:
                        name = name.replace(ch, '')
                    link = "https://shopee.tw/"+name + "-i."+str(shopid)+"."+str(itemid)
                # 運費內容爬蟲
                driver.get(link)
                # print(link)
                time.sleep(5)
                try:
                    element = driver.find_element_by_class_name(
                        '_35-eEv')  # 定位按鈕
                    ActionChains(driver).move_to_element(element).perform()
                    data1 = driver.page_source
                    soup = BeautifulSoup(data1, "html.parser")
                    market_fee = soup.select('div._1nxJbI')  # 運費版
                    ls_fee = []
                    min_cost_fee = 9999
                    for x in range(len(market_fee)):
                        market_name = market_fee[x].select('div.bCnGoL')[
                            0].text  # 商家名稱
                        if(market_name == "蝦皮店到店"):
                            continue
                        try:
                            shipping_fee = market_fee[x].select('div.qd9XVF')[
                                0].text  # 運費
                            if(shipping_fee == "免運費"):
                                min_cost_fee = 0
                            else:
                                shipping_fee = int(
                                    shipping_fee.replace("$", ""))
                                if(shipping_fee < min_cost_fee):
                                    min_cost_fee = shipping_fee

                        except:
                            shipping_fee = ''
                        try:
                            shipping_req = market_fee[x].select(
                                'div._3-jy5v')[0].text  # 運費需求
                        except:
                            shipping_req = ''
                        try:
                            others = market_fee[x].select('div._2Pry0u')[
                                0].text  # 其他事項
                        except:
                            others = ''
                        finally:
                            ls_fee.append(
                                [market_name, shipping_fee, shipping_req, others])

                    if(min_cost_fee == 9999):
                        min_cost_fee = "商品運費錯誤"
                        total_price = 9999
                    else:
                        total_price = int(price)+min_cost_fee
                    ls.append([name, price, link, str(shopid),
                               ls_fee, min_cost_fee, total_price])
                except:
                    print("商品無運送方式或錯誤")
        
        # except Exception as e:
        #    print(e)

        for i in range(len(ls)):
            ls[i][0] = ls[i][0].replace("/", "")

            # for i in range(len(ls)):
            # print(ls[i])
            # print(ls[i][0]) ##第i件商品名稱
            # print(ls[i][1]) ##第i件商品價錢
            # print(ls[i][2]) ##第i件商品link

            # 刪除原有資料
        doc_ref = db.collection('shopee', category, keyword).get()
        for doc in doc_ref:
            docs_fee = db.collection(
                'shopee', category, keyword, doc.id, 'fee').get()
            for fee in docs_fee:
                fee.reference.delete()
            doc.reference.delete()
            # print(ls)

        if(len(ls) == 0):
            doc_ref = db.collection(
                'shopee', category, keyword).document(keyword)
            myData = {
                'name': "null",
                'price': -1,
                'link': "null",
                'shopid': -1,
                'lowest_fee': -1,
                'total_price': -1
            }
            doc_ref.set(myData)
        else:
            for i in range(len(ls)):
                if ls[i][0] == '' or ls[i][1] == '' or ls[i][2] == '':
                    continue
                else:
                    # print(ls[i][0])
                    doc_ref = db.collection(
                        'shopee', category, keyword).document(ls[i][0])

                    myData = {
                        'name': ls[i][0],
                        'price': int(ls[i][1]),
                        'link': ls[i][2],
                        'shopid': int(ls[i][3]),
                        'lowest_fee': ls[i][5],
                        'total_price': ls[i][6]
                    }

                    doc_ref.set(myData)

                    for j in range(len(ls[i][4])):
                        doc_ref_1 = db.collection(
                            'shopee', category, keyword, ls[i][0], 'fee').document(str(j))

                        feeData = {
                            'name': ls[i][4][j][0],
                            'fee': ls[i][4][j][1],
                            'req': ls[i][4][j][2],
                            'others': ls[i][4][j][3]
                        }
                        # print(ls[i][4][j][0])
                        doc_ref_1.set(feeData)
                        # print(len(ls[i][4]))

        print(category + "--" + keyword + '已新增', len(ls), '筆資料')

driver.quit()
