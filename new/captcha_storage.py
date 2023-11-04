
import sys
import time
from selenium import webdriver

from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.happy-shopping.tw/login.php')
time.sleep(2)

element = driver.find_element_by_id("checkCode")
element.send_keys("")
session_id = driver.session_id
exe_id = driver.command_executor._url

#圖片截圖+裁切
from PIL import Image
png = driver.save_screenshot('ss.png')
im = Image.open("ss.png")
im = im.crop((877,279,1008,328))   #89 x 32
im.save('captcha.png','png')
im.close()


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from pyrebase import pyrebase


config = {
 "apiKey": "AIzaSyD7tE_NRFk7SenBFUkUCH3WgFdaKQcX304",
  "authDomain": "test-4fa88.firebaseapp.com",
  "databaseURL": "https://test-4fa88-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "test-4fa88",
  "storageBucket": "test-4fa88.appspot.com",
  "messagingSenderId": "951903532283",
  "appId": "1:951903532283:web:f88d9df405fd1db271ac5e",
  "measurementId": "G-Z8ZY003K1Z"
  }



firebase_storage = pyrebase.initialize_app(config)
storage = firebase_storage.storage()


for i in range(1, len(sys.argv)):
  index = sys.argv[i]
  
#index = 1234

name = "captcha"+str(index)

storage.child(name).put("captcha.png")


#print(session_id)
#print(exe_id)


cred = credentials.Certificate(r"test-4fa88-firebase-adminsdk-54nig-c645ede062.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection('driver_setting').document(index)

driver_data = {
  'id' : index,
  'session_id' : session_id,
  'exe_id' : exe_id,
}

doc_ref.set(driver_data)

