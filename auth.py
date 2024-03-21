# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash,session
from flask_login import login_user, logout_user, login_required
from models import User, db
import requests
import random, re
import os
from captcha.image import ImageCaptcha
from dotenv import load_dotenv
import mysql.connector
import string
import base64
import yagmail
from datetime import date, datetime
import time
import json
from threading import Thread
import threading
import locale


load_dotenv()


locale.setlocale(locale.LC_ALL, "Vi-VN")


image = ImageCaptcha(fonts=['/arial.ttf'])


auth = Blueprint('auth', __name__)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/naptien')
def napgame():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    if("_user_id" in session):
        user = User.query.get(int(session["_user_id"]))
        username = user.username
        id = session["_user_id"]
        mycursor.execute(f"SELECT vnd FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        bal="0đ"
        try:
            bal=locale.format_string("%d", int(result[0]), grouping=True) + "đ"
        except:
            pass
        agent = request.headers.get('User-Agent')
        phones = ["iphone", "android", "blackberry"]
        if any(phone in agent.lower() for phone in phones):
            mydb.close()
            dbnapthe.close()
            return render_template('napgame.html',user=username,bal=bal,phone=True)
        mydb.close()
        dbnapthe.close()
        return render_template('napgame.html',user=username,bal=bal)
    else:
        mydb.close()
        dbnapthe.close()
        return render_template('napgame.html')

@auth.route('/naptien',methods=['POST'])
def napgame_post():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    if("_user_id" in session):
        cash = request.form.get('cash')
        user = User.query.get(int(session["_user_id"]))
        username = user.username
        id = session["_user_id"]
        mycursor.execute(f"SELECT vnd FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        if not cash:
            flash("Vui lòng nhập số tiền muốn nạp trước")
        else:
            if not (cash.isdigit()):
                flash("Vui lòng nhập số")
            else:
                if(int(cash) > int(result[0])):
                    flash("Bạn không đủ tiền để nạp")
                elif(int(cash) < 1000):
                    flash("Tiền nạp tối thiểu 1.000đ")
                else:
                    mycursor.execute(f"SELECT tongnap, coin FROM account WHERE id = {id}")
                    re = mycursor.fetchone()
                    if(re):
                        mycursor.execute(f"UPDATE account SET tongnap = {str(int(re[0]) + int(cash))}, coin = {str(int(re[1]) + int(cash))} WHERE id = {id}")
                        mycursor.execute(f"UPDATE account SET vnd = {str(int(result[0]) - int(cash))} WHERE id = {id}")
                        mydb.commit()
                        flash("Nạp tiền thành công!")
                    else:
                        flash("Vui lòng tạo nhân vật trước khi nạp game!")
        bal="0đ"
        try:
            bal=locale.format_string("%d", int(result[0]) - int(cash), grouping=True) + "đ"
        except:
            pass
        agent = request.headers.get('User-Agent')
        phones = ["iphone", "android", "blackberry"]
        if any(phone in agent.lower() for phone in phones):
            mydb.close()
            dbnapthe.close()
            return render_template('napgame.html',user=username,bal=bal,phone=True)
        mydb.close()
        dbnapthe.close()
        return render_template('napgame.html',user=username,bal=bal)
    else:
        mydb.close()
        dbnapthe.close()
        return render_template('napgame.html')

@auth.route('/history')
def history():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    if("_user_id" in session):
        id = session["_user_id"]
        dbnapthe.commit()
        cur = dbnapthe.cursor()
        cur.execute(f"SELECT * FROM charge_history WHERE account_id={id}")
        result = cur.fetchall()
        newRel = []
        for rel in result:
            data = {"id": rel[0], "request_id": rel[2], "ammount": locale.format_string("%d", float(rel[5]), grouping=True) + "đ", "trangthai": str(rel[6]), "RealAmount": rel[7], "type":rel[8]}
            if rel[6] == 1:
                data["trangthai"] = "Thành Công"
            if rel[6] == 0:
                data["trangthai"] = "Đang Xử Lý"
            if rel[6] == 2:
                data["trangthai"] = "Thất Bại"
            if len(rel[7]) > 0:
                data["RealAmount"] = locale.format_string("%d", float(rel[7]), grouping=True) + "đ"
            else:
                data["RealAmount"] = "0đ"
            newRel.append(data)
        mydb.close()
        dbnapthe.close()
        return render_template('history.html',list=newRel)
    else:
        mydb.close()
        dbnapthe.close()
        return render_template('history.html')

@auth.route('/account')
def account():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    if("_user_id" in session):
        user = User.query.get(int(session["_user_id"]))
        username = user.username
        email = user.email
        id = session["_user_id"]
        mycursor.execute(f"SELECT vnd FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        bal="0đ"
        try:
            bal=locale.format_string("%d", result[0], grouping=True) + "đ"
        except:
            pass
        agent = request.headers.get('User-Agent')
        phones = ["iphone", "android", "blackberry"]
        if any(phone in agent.lower() for phone in phones):
            mydb.close()
            dbnapthe.close()
            return render_template('account.html', user=username, email=email, bal=bal, phone=True)
        mydb.close()
        dbnapthe.close()
        return render_template('account.html', user=username, email=email, bal=bal)
    else:
        mydb.close()
        dbnapthe.close()
        return render_template('account.html')

@auth.route('/napthe')
def napthe():
    return render_template('napthe.html')

@auth.route('/forget')
def forget():
    if('mail' in session):
        if(session["mail"]):
            return render_template('forgetPassword.html',femail = True)
    return render_template('forgetPassword.html')

@auth.route('/forget',methods=['POST'])
def forget_port():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    username = request.form.get('username')
    email = request.form.get('email')
    code = request.form.get('code')
    if(username or email):
        letters = string.ascii_lowercase
        captcha = ''.join(random.choice(letters) for i in range(6))
        if(username):
            user = User.query.filter_by(username=username).first()
            if(not user):
                flash("Không tìm thấy tài khoản!")
                mydb.close()
                dbnapthe.close()
                return redirect('/forget')
            #print(os.getenv("email") + os.getenv("pass"))
            #yag = yagmail.SMTP(user=os.getenv("email"), password=os.getenv("pass"))
            #yag.send(user.email, "Đổi Mật Khẩu", "Code của bạn là: " + captcha)
            session["code"] = captcha
            mydb.close()
            dbnapthe.close()
            return redirect('/forget',code=captcha)
        if(email):
            user = User.query.filter_by(email=email).first()
            if(not user):
                flash("Không tìm thấy tài khoản!")
                mydb.close()
                dbnapthe.close()    
                return redirect('/forget')
            #yag = yagmail.SMTP(user=os.getenv("email"), password=os.getenv("pass"))
            #yag.send(user.email, "Đổi Mật Khẩu", "Code của bạn là: " + captcha)
            session["code"] = captcha
            mydb.close()
            dbnapthe.close()
            return redirect('/forget',code=captcha)
    elif(code):
        if(code == session["code"]):
            newPass = request.form.get('newpass')
            mycursor.execute(f"UPDATE account SET password = {newPass} WHERE id = {user.id}")
            mydb.commit()
            flash("Đổi mật khẩu thành công!")
        else:
            flash("Sai Mã Code!")
    else:
        flash("Vui lòng điền đầy đủ thông tin")
    mydb.close()
    dbnapthe.close()
    return redirect('/forget')

@auth.route('/forgetm')
def forget2():
    if("mail" in session):
        session["mail"] = not session["mail"]
    else:
        session["mail"] = True
    return redirect('/forget')

@auth.route('/callback', methods=['POST'])
def napthe_callback():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    status = request.form.get('status')
    mess = request.form.get('message')
    request_id = request.form.get('request_id')
    cash = request.form.get('value')
    if(status == 1):
        dbnapthe.cursor().execute(f"SELECT account_id, id FROM charge_history WHERE status=0 AND request_id={request_id}")
        result = dbnapthe.cursor().fetchone()
        id = result[0]
        dbnapthe.cursor().execute(f"UPDATE charge_history SET status=1, RealAmount={cash} WHERE id={result[1]}")
        dbnapthe.commit()
        mycursor.execute(f"SELECT vnd FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        mycursor.execute(f"UPDATE account SET vnd = {str(int(result[0]) + int(cash))} WHERE id = {id}")
        #mycursor.execute(f"SELECT recharge, sotien FROM player WHERE account_id = {id}")
        #result = mycursor.fetchone()
        #mycursor.execute(f"UPDATE player SET recharge = {str(int(result[0]) + int(cash))}, sotien = {str(int(result[1]) + int(cash))} WHERE account_id = {id}")
        mydb.commit()
        #flash("Nạp Thẻ Thành Công!")
    elif(status == 2):
        cur = dbnapthe.cursor()
        cur.execute(f"SELECT account_id, id FROM charge_history WHERE status=0 AND request_id={request_id}")
        result = cur.fetchone()
        id = result[0]
        dbnapthe.cursor().execute(f"UPDATE charge_history SET status=1, RealAmount={cash} WHERE id={result[1]}")
        dbnapthe.commit()
        mycursor.execute(f"SELECT vnd FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        mycursor.execute(f"UPDATE account SET vnd = {str(int(result[0]) + int(cash/2))} WHERE id = {id}")
        #mycursor.execute(f"SELECT recharge, sotien FROM player WHERE account_id = {id}")
        #result = mycursor.fetchone()
        #mycursor.execute(f"UPDATE player SET recharge = {str(int(result[0]) + int(cash/2))}, sotien = {str(int(result[1]) + int(cash/2))} WHERE account_id = {id}")
        mydb.commit()
        #flash("Nạp Thẻ Thành Công Nhưng Sai Mệnh Giá!\nTrừ 1 nửa số tiền!")
    else:
        dbnapthe.cursor().execute(f"SELECT account_id, id FROM charge_history WHERE status=0 AND request_id={request_id}")
        result = dbnapthe.cursor().fetchone()
        id = result[0]
        dbnapthe.cursor().execute(f"UPDATE charge_history SET status=2, RealAmount=0 WHERE id={result[1]}")
        dbnapthe.commit()
    mydb.close()
    dbnapthe.close()
        #flash(mess)

@auth.route('/napthe', methods=['POST'])
def napthe_post():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    seri = request.form.get('seri')
    code = request.form.get('code')
    if(not seri.isnumeric() or not code.isnumeric()):
        flash('Số Seri và Mã Thẻ phải là số')
        mydb.close()
        dbnapthe.close()
        return redirect(url_for('auth.napthe'))
    cash = request.form.get('cash')
    thecao = request.form.get('thecao')
    if( seri is None or code is None):
        flash('Vui lòng nhập đủ thông tin')
        mydb.close()
        dbnapthe.close()
        return redirect(url_for('auth.napthe'))
    if(len(seri) < 5 or len(code) < 5):
        flash('Mã Thẻ hoặc Số Seri không đúng định dạng')
        mydb.close()
        dbnapthe.close()
        return redirect(url_for('auth.napthe'))
    request_id = random.randint(100000000,999999999)
    headers = {
        'Content-Type': 'application/json'
    }
    url = "https://gachthe1s.com/chargingws/v2"
    files = []
    payload={'telco': thecao,
    'code': str(code),
    'serial': str(seri),
    'amount': str(cash),
    'request_id': str(request_id),
    'partner_id': str(os.getenv("id")),
    'sign': str(os.getenv("key")),
    'command': 'charging'}
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    data = json.loads(response.text)
    if(data["status"] == 99):
        flash("Nạp thẻ thành công, vui lòng chờ duyệt!")
        id = session["_user_id"]
        dbnapthe.cursor().execute(f"INSERT INTO `charge_history`(`account_id`, `request_id`, `code`, `serial`, `amount`, `status`, `type`) VALUES ({id},{request_id},{code},{seri},{cash},0,\"THE CAO\")")
        dbnapthe.commit()
    elif data["status"] == 3:
        flash("Thẻ lỗi!")
    elif data["status"] == 4:
        flash("Hệ thống đang bảo trì!")
    elif data["status"] == 100:
        flash("Sai định dạng!")
    elif data["status"] == 102:
        flash("Sai seri hoặc mã thẻ!")
    else:
        flash(data["message"])
    print(seri + " " + code + " " + cash + " " + thecao + " " + str(data["status"]))
    mydb.close()
    dbnapthe.close()
    return redirect(url_for('auth.napthe'))

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(username=username).first()
    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not user.password == password:
        flash('Tài Khoản hoặc Mật Khẩu không hợp lệ')
        return redirect(url_for('auth.login'))  # if user doesn't exist or password is wrong, reload the page

    if not (re.fullmatch(regex, user.email)):
        flash('Email không hợp lệ')
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    flash('Đăng nhập thành công.')
    return redirect(url_for('main.index'))



@auth.route('/forum')
def forum():
    agent = request.headers.get('User-Agent')
    phones = ["iphone", "android", "blackberry"]
    if any(phone in agent.lower() for phone in phones):
        return render_template('forum.html', phone=True)
    return render_template('forum.html')


@auth.route('/bank')
def bank():
    link = os.getenv("link")
    mydb = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    mycursor = mydb.cursor()
    link = os.getenv("napthe")
    dbnapthe = mysql.connector.connect(
        host=link[(link.find("@")+1):(link.find(":",link.find("@")))],
        user=link[(link.find("//")+2):(link.find(":",link.find("//")))],
        password=link[(link.find(":",link.find(":")+1)+1):(link.find("@"))],
        database=link[link.rfind("/")+1:]
        )
    napcursor = dbnapthe.cursor()
    letters = string.ascii_lowercase
    result = True
    while result:
        captcha = ''.join(random.choice(letters) for i in range(5))
        napcursor.execute(f"SELECT * FROM charge_history WHERE code = \"{captcha}\"")
        result = napcursor.fetchone()
    id = session["_user_id"]
    mydb.close()
    dbnapthe.close()
    return render_template('napthe.html', bank=True, stk=os.getenv("accountNo"),description=f"BankNRO {captcha} {id}")
	

def getter():
    while True:
        url = f"https://online.mbbank.com.vn/api/retail-web-transactionservice/transaction/getTransactionAccountHistory"
        t = datetime.now()
        today = t.strftime("%d/%m/%Y")
        yd = int((t.strftime("%d"))) - 1
        day = str(yd)
        if yd < 10:
            day = "0"+str(yd)
        yesterday = day + t.strftime("/%m/%Y")
        timenow = t.strftime("%Y%m%d%H%M%S") + "00"
        dat = {"accountNo":os.getenv("accountNo"),"deviceIdCommon":os.getenv("deviceIdCommon"),"fromDate":yesterday,"refNo":os.getenv("account")+"-"+timenow,"sessionId":os.getenv("sessionId"),"toDate":today,"type":"ACCOUNT","historyType":"DATE_RANGE","historyNumber":""}
        header = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'vi-US,vi;q=0.9',
            'Authorization': 'Basic QURNSU46QURNSU4=',
            'Connection': 'keep-alive',
            'Host': 'online.mbbank.com.vn',
            'Origin': 'https://online.mbbank.com.vn',
            'Referer': 'https://online.mbbank.com.vn/information-account/source-account',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }
        response = requests.post(url, data=json.dumps(dat), headers=header)
        data = json.loads(response.text)
        if(data["transactionHistoryList"] is not None):
            print(str(data["transactionHistoryList"]) + "\n"+t.strftime("%Y/%m/%d %H:%M:%S"))
        else:
            print(str(data) + "\n"+t.strftime("%Y/%m/%d %H:%M:%S"))
        if data["transactionHistoryList"] is None:
            data["transactionHistoryList"] = []
        for dat in data["transactionHistoryList"]:
                if("BankNRO" in str(dat["description"])):
                    desc = str(dat["description"])
                    list = desc[desc.find("BankNRO "):].replace("BankNRO ","").split(" ")
                    uname = list[0]
                    id = int(list[1])
                    cash = dat["creditAmount"]
        time.sleep(90)
        
@auth.route('/register')
def register():
    letters = string.ascii_lowercase
    captcha = ''.join(random.choice(letters) for i in range(5))
    #img = image.generate(captcha)
    image.write(captcha, 'captcha.png')
    with open("captcha.png", "rb") as img_file:
        b64_string = base64.b64encode(img_file.read())
        b64_string = "data:image/png;base64,"+str(b64_string)[2:-1]
    session["captcha"] = captcha
    return render_template('register.html',img=b64_string)


@auth.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    cap = request.form.get('captcha')
    user = User.query.filter_by(email=email).first()  # if this returns a user, then the email already exists in database

    if(session["captcha"] != cap):
        flash('Sai captcha')
        return redirect(url_for('auth.register'))
    
    if user:  # if a user is found, we want to redirect back to register page so user can try again
        flash('Email đã tồn tại')
        return redirect(url_for('auth.register'))
    
    user = User.query.filter_by(username=username).first()
    
    if user:  # if a user is found, we want to redirect back to register page so user can try again
        flash('Username đã tồn tại')
        return redirect(url_for('auth.register'))
    
    if not (re.fullmatch(regex, email)):
        flash('Email không hợp lệ')
        return redirect(url_for('auth.register'))
    
    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(email=email, username=username, password=password)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    # code to validate and add user to database goes here
    flash('Đăng Ký Thành Công.')
    return redirect(url_for('auth.login')) 


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.')
    return redirect(url_for('main.index'))
