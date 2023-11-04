from flask import Flask, render_template, request, jsonify, redirect
import os,sys,json,subprocess,random
import time



app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/<name>', methods=['GET'])
def test1(name=None): 
    try:
        name = int(name)
    except:
        return render_template('index.html')
    
    if name == 1:
        return render_template('food_page.html',name=name)
    elif name == 2:
        return render_template('food_page_1.html',name=name)
    ##利用參數name來區分食譜 並將參數傳回html 利用js連接資料庫來讀取食譜資料

    return render_template('index.html',name=name)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/food_contents')
def food_contents():
    return render_template('food_contents.html')

@app.route('/food_page/<food_name>/<food_num>')
def food_page(food_name=None,food_num=None):
    return render_template('food_page.html',food_name=food_name,food_num=food_num)

@app.route('/Ingredient_contents')
def Ingredient_contents():
    return render_template('Ingredient_contents.html')

@app.route('/Ingredient_page/<Ing_name>/<Ing_num>')
def Ingredient_page(Ing_name=None,Ing_num=None):
    return render_template('Ingredient_page.html',Ing_name=Ing_name,Ing_num=Ing_num)

@app.route('/book_page')
def book_page():
    return render_template('book_page.html')

@app.route('/share_page')
def share_page():
    return render_template('share_page.html')

@app.route('/personal_page')
def personal_page():
    return render_template('personal_page.html')

@app.route('/main_login_page')
def main_login_page():
    return render_template('main_login_page.html')

@app.route('/choose_page', methods=['POST'])
def choose_page():
    index = random.randrange(0, 2147483647)
    txt = {"happyshopping":[],"pchome":[],"shopee":[]}
    
    products = request.form.getlist('product')
    
    print(products)
    '''
    for i in range(len(products)):
        
        query_rs = subprocess.check_output("python happyshopping_find_products.py "+products[i]).decode("ascii")
        query_rs = query_rs.replace('\r\n','')
        query_rs = eval(query_rs)
        txt["happyshopping"].append({"name":query_rs[0].decode(),"price":query_rs[1],"category":query_rs[2].decode(),"prod":products[i],"link":query_rs[3].decode()})
        
        query_pchome = subprocess.check_output("python pchome_find_products.py "+products[i]).decode("ascii")   
        query_pchome = query_pchome.replace('\r\n','')
        query_pchome = eval(query_pchome)     
        txt["pchome"].append({"name":query_pchome[0].decode(),"price":query_pchome[1],"category":query_pchome[2].decode(),"prod":products[i],"link":query_pchome[3].decode()})
        
        query_shopee = subprocess.check_output("python shopee_find_products.py "+products[i]).decode("ascii")   
        query_shopee = query_shopee.replace('\r\n','')
        query_shopee = eval(query_shopee)
        txt["shopee"].append({"name":query_shopee[0].decode(),"price":query_shopee[1],"category":query_shopee[2].decode(),"prod":products[i],"link":query_shopee[3].decode()})
    ''' 

    p=""
    for i in range(len(products)):
        p +=products[i]+" "
    
    query_happyshopping = subprocess.check_output("python happyshopping_find_products.py "+p).decode("ascii")
    print(query_happyshopping)
    query_happyshopping = query_happyshopping.replace('\r\n','')
    query_happyshopping = query_happyshopping.replace(']','],')
    query_happyshopping = eval(query_happyshopping)
    for i in range(len(query_happyshopping)):
        txt["happyshopping"].append({"name":query_happyshopping[i][0].decode(),"price":query_happyshopping[i][1],"category":query_happyshopping[i][2].decode(),"prod":query_happyshopping[i][3].decode(),"link":query_happyshopping[i][4].decode()})
    
    query_pchome = subprocess.check_output("python pchome_find_products.py "+p).decode("ascii")
    query_pchome = query_pchome.replace('\r\n','')
    query_pchome = query_pchome.replace(']','],')
    query_pchome = eval(query_pchome)
    for i in range(len(query_pchome)):
        txt["pchome"].append({"name":query_pchome[i][0].decode(),"price":query_pchome[i][1],"category":query_pchome[i][2].decode(),"prod":query_pchome[i][3].decode(),"link":query_pchome[i][4].decode()})

    query_shopee = subprocess.check_output("python shopee_find_products.py "+p).decode("ascii")
    query_shopee = query_shopee.replace('\r\n','')
    query_shopee = query_shopee.replace(']','],')
    query_shopee = eval(query_shopee)
    for i in range(len(query_shopee)):
        txt["shopee"].append({"name":query_shopee[i][0].decode(),"price":query_shopee[i][1],"category":query_shopee[i][2].decode(),"prod":query_shopee[i][3].decode(),"link":query_shopee[i][4].decode(),"lowest_fee":query_shopee[i][5],"total_price":query_shopee[i][6],"shopid":query_shopee[i][7]})


    print(txt)
    print(index)
    return render_template('choose_page.html',products=txt,index =index)

@app.route('/choose_page_no2')
def choose_page_no2():
    return render_template('choose_page_no2.html')

@app.route('/login_page', methods=['POST'])
def login(id=None):
    log = request.form.getlist('box')
    index = request.form['index']
    #print(log[0])
    print(index)
    #index = random.randrange(0, 2147483647)
    # i = subprocess.check_output("python captcha_storage.py "+str(index)).decode("ascii")
    if log[0]=="1":
        i = subprocess.Popen("python captcha_storage.py "+str(index))
        i.wait()
        time.sleep(1)
        return render_template('login_page_1.html',id=index)
    elif log[0]=="2":
        time.sleep(1)
        return render_template('login_page_2.html',id=index)
    elif log[0]=="3":
        time.sleep(1)
        return render_template('login_page_3.html',id=index)



@app.route('/result', methods=['POST'])
def result(id=None, account=None, pw=None, pic=None):
    
    login_index = request.form['login_index'] ##商場辨識碼 1=熊 2=pchome 3=shopee
    id =request.form['new_id']
    account = request.form['account']
    pw = request.form['passwd']


    ## i 來決定程式是否報錯 0 = 成功執行; 1 = 錯誤
    if login_index=="1":
        pic = request.form['captcha']
        i = subprocess.Popen("python happyshopping_login.py "+id+" "+account+" "+pw+" "+pic)
        i.wait()
        if i.returncode ==1:
            j = subprocess.Popen("python captcha_storage.py "+id)
            j.wait()
            
            return render_template('login_page_1.html',id=id)
        else:
            return redirect('https://www.happy-shopping.tw/cart.php')
    elif login_index=="2":
        i = subprocess.Popen("python pchome_login.py "+id+" "+account+" "+pw)
        i.wait()
        if i.returncode ==1:
            return render_template('login_page_2.html',id=id)
        else:
            return redirect('https://ecssl.pchome.com.tw/sys/cflow/fsindex/BigCar/BIGCAR/ItemList')
    elif login_index=="3":
        i = subprocess.Popen("python shopee_login.py "+id+" "+account+" "+pw)
        i.wait()
        if i.returncode ==1:
            return render_template('login_page_3.html',id=id)
        else:
            return redirect('https://shopee.tw/cart') 




if __name__ == '__main__':
    app.run(host='140.119.19.13',port=80,debug = True)
    #app.run(ssl_context='adhoc')
    #app.run(host='140.119.19.13',port=80,debug = True , ssl_context=('/Users/user/Desktop/new/server.crt', '/Users/user/Desktop/new/server.key'))
    #from waitress import serve
    #serve(app, host="0.0.0.0", port=80 , ssl_context='adhoc')
