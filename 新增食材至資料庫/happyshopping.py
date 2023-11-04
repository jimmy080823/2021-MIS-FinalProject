'''
input: 輸入食材種類 or 食材名稱(名稱需要出現在下面list內)
-1 => 更新全部種類食材
'''
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from selenium.webdriver.chrome.options import Options
import jieba


cred = credentials.Certificate(r"test-4fa88-firebase-adminsdk-54nig-c645ede062.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
chrome_options = Options()
chrome_options.add_argument("--headless")
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

black_list = ["五桔國際","快樂大廚義式醬汁","寶寶米餅","貓貓"]

def categories(keyword:str)->str:
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

def duplicate_check(data:list)->list:
  for i in range(len(data)-1):
    if(data[i]==data[i+1]):
        data[i]=""             
  while "" in data:
    data.remove("")
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
    #blackList Test
    for j in range(len(black_list)):
      if seg_list[i] == black_list[j]:
        return False

    if seg_list[i] == key:
      print(seg_list,"True")
      return True
  #print(seg_list,"False")
  return False

driver = webdriver.Chrome(options=chrome_options)

while(True):

  keyword = input("請輸入關鍵字/種類:")

  ##預搜索種類/單一產品轉換為list

  #蔬菜類
  if(keyword=="蔬菜"):
    search = vegetable_list
  elif(keyword=="水果"):
    search = fruit_list
  elif(keyword=="調味料"):
    search = seasoning_list
  elif(keyword=="肉類"):
    search = meat_list
  elif(keyword=="海鮮"):
    search = seafood_list
  elif(keyword=="其他"):
    search = others
  elif(keyword=="主食"):
    search = grains_list
  elif(keyword=="-1"):
    search = vegetable_list+fruit_list+seasoning_list+meat_list+seafood_list+others+grains_list
  #單一產品
  else:
    search = [keyword]
    


  for x in range(len(search)):

    
    #初始化
    count = 0                             ##重爬次數
    search_available = False  ##檢測是否能爬到東西
    name =[]
    price = []
    urls = []
    ls = []
    category = categories(search[x])
    keyword = search[x]
    
    while (search_available==False):
      try:
      ##前往網址&卷軸
        url = 'https://www.happy-shopping.tw/search_list.php?qry='+urllib.parse.quote(search[x], safe='')
        driver.get(url)
        time.sleep(1)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
          driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
          time.sleep(1)
          new_height = driver.execute_script("return document.body.scrollHeight")
          time.sleep(2.5)
          if new_height == last_height:
              break
          last_height = new_height

        data = driver.page_source
        soup = BeautifulSoup(data,"html.parser")
        product_tag = soup.select('li div.item')   ##關鍵字所得出的商品
      except:
        count+=1
      ##重爬檢測

      if count>=5:
        search_available = True
        #print("##############食材找不到 重試已達五次-----------",search[x])
      elif len(product_tag)!=0:
        search_available = True
        #print("有東西")
      else:
        count+=1
        #print("沒東西",count)
        
      ##全部產品相關標籤
      for i in range(len(product_tag)):
        cart = product_tag[i].select("a.uhide")
        ##產品缺貨則continue
        if cart:
          continue
        else:
          name.append(product_tag[i].select("a.prod_name p")[0].text)
          price.append(product_tag[i].select("span.discount")[0].text)
          link = product_tag[i].select_one("a")['href']
          urls.append("https://www.happy-shopping.tw/"+link)
        
      try:
        for i in range(len(name)):
          if (jiebaFilter(name[i],search[x])==True):
            ls.append([name[i],price[i],urls[i]])
      except:
        print("例外處理")
      ls.sort()
      ls = duplicate_check(ls)


    for i in range (len(ls)):
      ls[i][0]= ls[i][0].replace("/","")
      ls[i][1]= ls[i][1].replace("$","")

    ##資料庫的部分


    #刪除原有資料
    doc_ref = db.collection('happyshopping',category,keyword).get()
    for doc in doc_ref:
      doc.reference.delete()

    #如果搜尋不到 length of list = 0, 新增null資訊
    #print(ls)
    if(len(ls)==0):
        doc_ref = db.collection('happyshopping',category,keyword).document(keyword)
        myData={
          'name': 'null',
          'price': '-1',
          'link': 'null',}

        doc_ref.set(myData)
    #新增
    for i in range(len(ls)):
      if ls[i][0] =='' or ls[i][2] =='':
        continue

      else:
        #print(ls[i][0])
        doc_ref = db.collection('happyshopping',category,keyword).document(ls[i][0])
      
        myData={
        'name': ls[i][0],
        'price': int(ls[i][1]),
        'link': ls[i][2],}

        doc_ref.set(myData)

      
    print(category,'-',keyword,'   已新增',len(ls),'筆資料')

