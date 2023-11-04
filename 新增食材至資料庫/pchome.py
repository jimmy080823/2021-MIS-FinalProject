'''
input: 輸入食材種類 or 食材名稱(名稱需要出現在下面list內)

-1 => 更新全部種類食材
'''


import time
import json
import random
import requests
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import jieba

'''
食材分類
'''
vegetable_list = ["杏鮑菇","金針菇","香菇","地瓜葉","小白菜","高麗菜","青江菜","菠菜","油菜","娃娃菜","大陸妹","花椰菜","莧菜","牛蒡","洋蔥","紅蘿蔔","馬鈴薯","玉米筍","白蘿蔔","番茄","秀珍菇","木耳","小黃瓜","大黃瓜","櫛瓜","辣椒","青椒","甜椒","玉米","南瓜","芹菜","泡菜","海帶"]
fruit_list = ["鳳梨","蘋果","香蕉","檸檬"]
seasoning_list = ["九層塔","薑","黑胡椒","醬油","白糖","紅糖","醋","糯米醋","橄欖油","味噌","番茄醬","蔥","蔥花","沙拉油","麻油","冰糖","豆瓣醬","奶油","白醋","鹽","五香粉","美乃滋","烏醋","味醂","香油","白胡椒粉","沙拉醬","凱薩醬","紅椒粉","芥末醬","魚露","香茅","花椒","蜂蜜","黑麻油"]
meat_list = ["牛肉","豬肉","羊肉","雞肉","肉片","半雞","全雞","豬絞肉","肉絲","雞腿","雞胸","雞翅","牛肉塊","豬肉塊","雞肉塊","肉醬","牛絞肉","培根","五花肉片","牛五花肉","豬五花肉"]
seafood_list = ["蝦仁","蝦子","小卷","章魚","透抽","草蝦","白蝦","吳郭魚","白鯧魚","秋刀魚","鮪魚","鮭魚","柳葉魚","旗魚","虱目魚","沙丁魚","黃魚","鯖魚","吻仔魚","螃蟹","蟹肉","干貝","花枝","小管","魚卵","帆立貝","螺肉","蜆","海瓜子","比目魚","海膽","魷魚","蛤"]
others = ["樹薯粉","地瓜粉","太白粉","豆腐","雞蛋","肉鬆","起司","糯米粉","玉米粉","抹茶粉","可可粉","杏仁片","牛奶","泡打粉","巧克力","杏仁","杏仁粉","月桂葉","咖哩","綠咖哩","中筋麵粉","低筋麵粉","蒜頭","麵粉"]
grains_list =["米","烏龍麵","米粉","冬粉","義大利麵","筆管麵","吐司","麵包","漢堡麵包"]

black_list = ["五桔國際","快樂大廚義式醬汁"]


class PchomeSpider():
    """PChome線上購物 爬蟲"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
        }

    def request_get(self, url, params=None, to_json=True):
        """送出 GET 請求

        :param url: 請求網址
        :param params: 傳遞參數資料
        :param to_json: 是否要轉為 JSON 格式
        :return data: requests 回應資料
        """
        r = requests.get(url, params)
        #print(r.url)
        if r.status_code != requests.codes.ok:
            print()
            #print(f'網頁載入發生問題：{url}')
        try:
            if to_json:
                data = r.json()
            else:
                data = r.text
        except Exception as e:
            #print(e)
            return None
        return data

    def search_products(self, keyword, max_page=1, shop='全部', sort='有貨優先', price_min=-1, price_max=-1,
                        is_store_pickup=False, is_ipost_pickup=False):
        """搜尋商品

        :param keyword: 搜尋關鍵字
        :param max_page: 抓取最大頁數
        :param shop: 賣場類別 (全部、24h購物、24h書店、廠商出貨、PChome旅遊)
        :param sort: 商品排序 (有貨優先、精準度、價錢由高至低、價錢由低至高、新上市)
        :param price_min: 篩選"最低價" (需與 price_max 同時用)
        :param price_max: 篩選"最高價" (需與 price_min 同時用)
        :param is_store_pickup: 篩選"超商取貨"
        :param is_ipost_pickup: 篩選"i 郵箱取貨"
        :return products: 搜尋結果商品
        """
        products = []
        all_shop = {
            '全部': 'all',
            '24h購物': '24h',
            '24h書店': '24b',
            '廠商出貨': 'vdr',
            'PChome旅遊': 'tour',
        }
        all_sort = {
            '有貨優先': 'sale/dc',
            '精準度': 'rnk/dc',
            '價錢由高至低': 'prc/dc',
            '價錢由低至高': 'prc/ac',
            '新上市': 'new/dc',
        }

        url = f'https://ecshweb.pchome.com.tw/search/v3.3/{all_shop[shop]}/results'
        params = {
            'q': keyword,
            'sort': all_sort[sort],
            'page': 0
        }
        if price_min >= 0 and price_max >= 0:
            params['price'] = f'{price_min}-{price_max}'
        if is_store_pickup:
            params['cvs'] = 'all'  # 超商取貨
        if is_ipost_pickup:
            params['ipost'] = 'Y'  # i 郵箱取貨

        while params['page'] < max_page:
            params['page'] += 1
            data = self.request_get(url, params)
            if not data:
                #print(f'請求發生錯誤：{url}{params}')
                break
            if data['totalRows'] <= 0:
                #print('找不到有關的產品')
                break
            products.extend(data['prods'])
            if data['totalPage'] <= params['page']:
                break
        return products

    def get_products_sale_status(self, products_id):
        """取得商品販售狀態

        :param products_id: 商品 ID
        :return data: 商品販售狀態資料
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={products_id}'
        data = self.request_get(url)
        if not data:
            #print(f'請求發生錯誤：{url}')
            return []
        return data

    def get_products_specification(self, products_id):
        """取得商品規格種類

        :param products_id: 商品 ID
        :return data: 商品規格種類
        """
        if type(products_id) == list:
            products_id = ','.join(products_id)
        url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/spec&id={products_id}&_callback=jsonpcb_spec'
        data = self.request_get(url, to_json=False)
        # 去除前後 JS 語法字串
        data = json.loads(data[17:-48])
        return data

    def get_search_category(self, keyword):
        """取得搜尋商品分類(網頁左側)

        :param keyword: 搜尋關鍵字
        :return data: 分類資料
        """
        url = f'https://ecshweb.pchome.com.tw/search/v3.3/all/categories?q={keyword}'
        data = self.request_get(url)
        return data

    def get_search_categories_name(self, categories_id):
        """取得商品子分類的名稱(網頁左側)

        :param categories_id: 分類 ID
        :return data: 子分類名稱資料
        """
        if type(categories_id) == list:
            categories_id = ','.join(categories_id)
        url = f'https://ecapi-pchome.cdn.hinet.net/cdn/ecshop/cateapi/v1.5/store&id={categories_id}&fields=Id,Name'
        data = self.request_get(url)
        return data

def jiebaFilter(product:str,key:str)->bool:

    
    for ch in ['(',')',' ','【','】']:
        if ch in product:
            product = product.replace(ch,'')
    
    text = [product]
    jieba.load_userdict('addDict.txt')

    f = open('delDict.txt', 'r',encoding = 'utf-8')
    for line in f.readlines():
        line = line.replace('\n','')
        jieba.del_word(line)
    f.close()
    
    for sentence in text:
        seg_list = jieba.lcut(sentence, cut_all=False)    
    for i in range(len(seg_list)):
        if seg_list[i] == key:
            print(seg_list,"True")
            return True
    #print(seg_list,"False")
    return False


def categories(prod:str):
        for i in range(len(vegetable_list)):
            if prod == vegetable_list[i]:
                return "蔬菜"
        for i in range(len(fruit_list)):
            if prod == fruit_list[i]:
              return "水果"
        for i in range(len(seasoning_list)):
            if prod == seasoning_list[i]:
              return "調味料"
        for i in range(len(meat_list)):
            if prod == meat_list[i]:
              return  "肉類"
        for i in range(len(seafood_list)):
            if prod == seafood_list[i]:
              return  "海鮮"
        for i in range(len(others)):
            if prod == others[i]:
              return  "其他"
        for i in range(len(grains_list)):
            if prod == grains_list[i]:
              return  "主食"
    
#--------------------重要區塊--------------------------
if __name__ == '__main__':

    ##db區間
    cred = credentials.Certificate(r"test-4fa88-firebase-adminsdk-54nig-c645ede062.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()



    
    while True:
        pchome_spider = PchomeSpider()
        prod = input("請輸入關鍵字:") #品項

        if(prod=="蔬菜"):
            search = vegetable_list
        elif(prod=="水果"):
            search = fruit_list
        elif(prod=="調味料"):
             search = seasoning_list
        elif(prod=="肉類"):
            search = meat_list
        elif(prod=="海鮮"):
             search = seafood_list
        elif(prod=="其他"):
            search = others
        elif(prod=="主食"):
            search = grains_list
        elif(prod=="-1"):
            search = vegetable_list+fruit_list+seasoning_list+meat_list+seafood_list+others+grains_list
        else:
            search = [prod]


            
        for x in range(len(search)):
            count=0
            prod = search[x]
            category = categories(search[x])
            
            key = prod +" "+ category
            #print(prod + category)
            
            # products = pchome_spider.search_products(keyword='手機', shop='24h購物', sort='價錢由高至低', price_min=0, price_max=5000)
            # print(len(products))
            try:
                products = pchome_spider.search_products(keyword=key, sort ='精準度', max_page=5)
            except:
                print(len(products))
            while (len(products)==0):
                time.sleep(2)
                try:
                    products = pchome_spider.search_products(keyword=key, sort ='精準度', max_page=15)
                except:
                    print()
                count +=1
                if count >=5:
                    print("###################產品錯誤高達五次------------------",key)
                    break
        
            #excel_file = Workbook()
            #sheet = excel_file.active
            #sheet['A1'] = '品項'
            #sheet['B1'] = '品名'
            #sheet['C1'] = '份量'
            #sheet['D1'] = '價錢'

            p1 = re.compile(r'[(](.*?)[)]', re.S)
            p2 = re.compile(r'[(](.*)[)]', re.S)
            my_regex = " \(.*\)|\s-\s.* "

            ls = []
            
            for i in range(len(products)):    #此處為show出關鍵字爬蟲後列表
                if (jiebaFilter(products[i]['name'],prod)==True):
                    ls.append([products[i]['name'],products[i]['price'],products[i]['Id']])
                    #print('品名: ' + products[i]['name'] + ' 份量: ' + " ".join(re.findall(p2, products[i]['name'])) + '  價錢: ' + str(products[i]['price']) + ' 網址: ' + products[i]['Id'])
                    #print('==========')

        #---------------db區間-------------------------------------------

            #刪除原有資料
            doc_ref = db.collection('pchome',category,prod).get()
            for doc in doc_ref:
                doc.reference.delete()

            #如果搜尋不到 length of list = 0, 新增null資訊

            if(len(ls)==0):
                doc_ref = db.collection('pchome',category,prod).document(prod)
                myData={
                'name': 'null',
                'price': '-1',
                'link': 'null',}

                doc_ref.set(myData)
                
            for i in range(len(ls)):
                #title = eval(repr( ls[i]['name']).replace('/', '|'))
                ls[i][0] = ls[i][0].replace('/','|')
                 #選擇路徑
                doc_ref = db.collection('pchome',category,prod).document(ls[i][0])
                
                 #新增/修改
                data = {
                    'name':(ls[i][0]),
                    'price':(ls[i][1]),
                    'link':('https://24h.pchome.com.tw/prod/' + ls[i][2]),
                }
                #print(data)
                #print(ls[i][0])
                doc_ref.set(data)
            print(category + "--" + prod + "  已新增  " + str(len(ls)) + " 筆資料")


