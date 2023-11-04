from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import urllib
import re
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import sys

vegetable_list = ["杏鮑菇","金針菇","香菇","地瓜葉","小白菜","高麗菜","青江菜","菠菜","油菜","娃娃菜","大陸妹","花椰菜","莧菜","牛蒡","洋蔥","紅蘿蔔","馬鈴薯","玉米筍","白蘿蔔","番茄","秀珍菇","木耳","小黃瓜","大黃瓜","櫛瓜","辣椒","青椒","甜椒","玉米","南瓜","芹菜","泡菜","海帶"]
fruit_list = ["鳳梨","蘋果","香蕉","檸檬"]
seasoning_list = ["九層塔","薑","黑胡椒","醬油","白糖","紅糖","醋","糯米醋","橄欖油","味噌","番茄醬","蔥","蔥花","沙拉油","麻油","冰糖","豆瓣醬","奶油","白醋","鹽","五香粉","美乃滋","烏醋","味醂","香油","白胡椒粉","沙拉醬","凱薩醬","紅椒粉","芥末醬","魚露","香茅","花椒","蜂蜜","黑麻油"]
meat_list = ["牛肉","豬肉","羊肉","雞肉","肉片","半雞","全雞","豬絞肉","肉絲","雞腿","雞胸","雞翅","牛肉塊","豬肉塊","雞肉塊","肉醬","牛絞肉","培根","五花肉片","牛五花肉","豬五花肉"]
seafood_list = ["蝦仁","蝦子","小卷","章魚","透抽","草蝦","白蝦","吳郭魚","白鯧魚","秋刀魚","鮪魚","鮭魚","柳葉魚","旗魚","虱目魚","沙丁魚","黃魚","鯖魚","吻仔魚","螃蟹","蟹肉","干貝","花枝","小管","魚卵","帆立貝","螺肉","蜆","海瓜子","比目魚","海膽","魷魚","蛤"]
others = ["樹薯粉","地瓜粉","太白粉","豆腐","雞蛋","肉鬆","起司","糯米粉","玉米粉","抹茶粉","可可粉","杏仁片","牛奶","泡打粉","巧克力","杏仁","杏仁粉","月桂葉","咖哩","綠咖哩","中筋麵粉","低筋麵粉","蒜頭","麵粉"]
grains_list =["米","烏龍麵","米粉","冬粉","義大利麵","筆管麵","吐司","麵包","漢堡麵包"]

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

cred = credentials.Certificate(r"test-4fa88-firebase-adminsdk-54nig-c645ede062.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def order(keyword):
  try:
    category = categories(keyword)
    doc_ref = db.collection('shopee',category,keyword)
    list = doc_ref.get()
    for doc in list:
        name = doc.to_dict()['name']
    priceQ = doc_ref.order_by(u'total_price', direction = firestore.Query.ASCENDING).limit_to_last(1)
    Plist = priceQ.get()

    ls = []


    for doc in Plist:
        name = doc.to_dict()['name']
        price = doc.to_dict()['price']
        link = doc.to_dict()['link']
        lowest_fee = doc.to_dict()['lowest_fee']
        total_price = doc.to_dict()['total_price']
        shopid = doc.to_dict()['shopid']
        ls.append(name.encode())
        ls.append(price)
        ls.append(category.encode())
        ls.append(keyword.encode())
        ls.append(link.encode())
        ls.append(lowest_fee)
        ls.append(total_price)
        ls.append(shopid)
        print(ls)
  except:
    ls.append(keyword.encode())
    ls.append(-1)
    ls.append("".encode())
    ls.append("".encode())
    ls.append("".encode())
    ls.append("")
    ls.append("")
    ls.append("")
    print(ls)

for i in range(1, len(sys.argv)):
  order(sys.argv[i])









