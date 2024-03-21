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
import json
import time as timer

load_dotenv()

mydb = mysql.connector.connect(
  host=os.getenv("link")[22:31],
  user=os.getenv("link")[8:12],
  password=os.getenv("link")[13:21],
  database=os.getenv("link")[37:len(os.getenv("link"))]
)

dbnapthe = mysql.connector.connect(
  host=os.getenv("napthe")[22:31],
  user=os.getenv("napthe")[8:12],
  password=os.getenv("napthe")[13:21],
  database=os.getenv("napthe")[37:len(os.getenv("napthe"))]
)

mycursor = mydb.cursor()

image = ImageCaptcha(fonts=['/arial.ttf'])


auth = Blueprint('auth', __name__)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

@auth.route('/login')
def login():
    return render_template('login.html')

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
    username = request.form.get('username')
    email = request.form.get('email')
    code = request.form.get('code')
    if(username or email):
        letters = string.ascii_lowercase
        captcha = ''.join(random.choice(letters) for i in range(6))
        print(username)
        if(username):
            user = User.query.filter_by(username=username).first()
            if(not user):
                flash("Không tìm thấy tài khoản!")
                return redirect('/forget')
            #print(os.getenv("email") + os.getenv("pass"))
            yag = yagmail.SMTP(user=os.getenv("email"), password=os.getenv("pass"))
            yag.send(user.email, "Đổi Mật Khẩu", "Code của bạn là: " + captcha)
            session["code"] = captcha
            return redirect('/forget',code=captcha)
        if(email):
            user = User.query.filter_by(email=email).first()
            if(not user):
                flash("Không tìm thấy tài khoản!")
                return redirect('/forget')
            yag = yagmail.SMTP(user=os.getenv("email"), password=os.getenv("pass"))
            yag.send(user.email, "Đổi Mật Khẩu", "Code của bạn là: " + captcha)
            session["code"] = captcha
            return redirect('/forget',code=captcha)
        print(email)
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
    status = request.form.get('status')
    mess = request.form.get('message')
    request_id = request.form.get('request_id')
    cash = request.form.get('value')
    if(status == 1):
        dbnapthe.cursor().execute(f"SELECT account_id, id FROM charge_history WHERE status=0, request_id={request_id}")
        result = dbnapthe.cursor().fetchone()
        id = result[0]
        dbnapthe.cursor().execute(f"UPDATE charge_history SET status=1, RealAmount={cash} WHERE id={result[1]}")
        dbnapthe.commit()
        mycursor.execute(f"SELECT balance FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        mycursor.execute(f"UPDATE account SET balance = {int(result[0] + cash)} WHERE id = {id}")
        mycursor.execute(f"SELECT recharge, sotien FROM player WHERE account_id = {id}")
        result = mycursor.fetchone()
        mycursor.execute(f"UPDATE player SET recharge = {int(result[0] + cash)}, sotien = {int(result[1] + cash)} WHERE account_id = {id}")
        mydb.commit()
        flash("Nạp Thẻ Thành Công!")
    elif(status == 2):
        dbnapthe.cursor().execute(f"SELECT account_id, id FROM charge_history WHERE status=0, request_id={request_id}")
        result = dbnapthe.cursor().fetchone()
        id = result[0]
        dbnapthe.cursor().execute(f"UPDATE charge_history SET status=1, RealAmount={cash} WHERE id={result[1]}")
        dbnapthe.commit()
        mycursor.execute(f"SELECT balance FROM account WHERE id = {id}")
        result = mycursor.fetchone()
        mycursor.execute(f"UPDATE account SET balance = {int(result[0] + (cash/2))} WHERE id = {id}")
        mycursor.execute(f"SELECT recharge, sotien FROM player WHERE account_id = {id}")
        result = mycursor.fetchone()
        mycursor.execute(f"UPDATE player SET recharge = {int(result[0] + (cash/2))}, sotien = {int(result[1] + (cash/2))} WHERE account_id = {id}")
        mydb.commit()
        flash("Nạp Thẻ Thành Công Nhưng Sai Mệnh Giá!\nTrừ 1 nửa số tiền!")
    else:
        flash(mess)

@auth.route('/napthe', methods=['POST'])
def napthe_post():
    seri = request.form.get('seri')
    code = request.form.get('code')
    if(not seri.isnumeric() or not code.isnumeric()):
        flash('Số Seri và Mã Thẻ phải là số')
        return redirect(url_for('auth.napthe'))
    cash = request.form.get('cash')
    thecao = request.form.get('thecao')
    if( seri is None or code is None):
        flash('Vui lòng nhập đủ thông tin')
        return redirect(url_for('auth.napthe'))
    if(len(seri) < 5 or len(code) < 5):
        flash('Mã Thẻ hoặc Số Seri không đúng định dạng')
        return redirect(url_for('auth.napthe'))
    request_id = random.randint(100000000,999999999)
    headers = {
        'Content-Type': 'application/json'
    }
    url = "http://gachthe1s.com/chargingws/v2"
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
    if(response["status"] == 99):
        flash("Nạp thẻ thành công, vui lòng chờ duyệt!")
        id = session["_user_id"]
        dbnapthe.cursor().execute(f"INSERT INTO `charge_history`(`account_id`, `request_id`, `code`, `serial`, `amount`, `status`, `type`) VALUES ({id},{request_id},{code},{seri},{cash},0,\"THE CAO\")")
        dbnapthe.commit()
    elif response["status"] == 3:
        flash("Thẻ lỗi!")
    elif response["status"] == 4:
        flash("Hệ thống đang bảo trì!")
    elif response["status"] == 100:
        flash("Sai định dạng!")
    else:
        flash(response["message"])
    print(seri + " " + code + " " + cash + " " + thecao)
    return redirect(url_for('auth.napthe'))

@auth.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(username=username).first()
    print(username, password, flush=True)
    print(user, flush=True)
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



@auth.route('/bank')
def bank():
    #letters = string.ascii_lowercase
    #bank = ''.join(random.choice(letters) for i in range(5))
    return render_template('napthe.html', bank=True)


@auth.route('/bank', methods=['POST'])
def bank_post():
    cash = request.form.get('cash')
    if(cash):
        letters = string.ascii_lowercase
        captcha = ''.join(random.choice(letters) for i in range(5))
        session["bankCode"] = captcha
        session["SelCash"] = cash
        return render_template('napthe.html', bank=True, value=cash,stk=os.getenv("accountNo"),description=captcha)
    else:
        mk = os.getenv("mkMB")
        token = os.getenv("token")
        stk = os.getenv("stkMB")
        url = f"https://online.mbbank.com.vn/api/retail-web-transactionservice/transaction/getTransactionAccountHistory"
        time = datetime.now()
        today = time.strftime("%d/%m/%Y")
        timenow = time.strftime("%Y%m%d%H%M%S") + "00"
        dat = {"accountNo":os.getenv("accountNo"),"deviceIdCommon":os.getenv("deviceIdCommon"),"fromDate":today,"refNo":os.getenv("account")+"-"+timenow,"sessionId":os.getenv("sessionId"),"toDate":today,"type":"ACCOUNT","historyType":"DATE_RANGE","historyNumber":""}
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
        check = False
        for dat in data["transactionHistoryList"]:
            if(dat["description"] == session["bankCode"]):
                selCash = session["SelCash"]
                cash = dat["creditAmount"]
                request_id = random.randint(100000000,999999999)
                id = session["_user_id"]
                dbnapthe.cursor().execute(f"INSERT INTO `charge_history`(`account_id`, `request_id`, `amount`, `RealAmount`, `status`, `type`) VALUES ({id},{request_id},{selCash},{cash},1,\"MB Bank\")")
                dbnapthe.commit()
                mycursor.execute(f"SELECT balance FROM account WHERE id = {id}")
                result = mycursor.fetchone()
                mycursor.execute(f"UPDATE account SET balance = {int(result[0] + cash)} WHERE id = {id}")
                mycursor.execute(f"SELECT recharge, sotien FROM player WHERE account_id = {id}")
                result = mycursor.fetchone()
                mycursor.execute(f"UPDATE player SET recharge = {int(result[0] + cash)}, sotien = {int(result[1] + cash)} WHERE account_id = {id}")
                mydb.commit()
                check = True
                flash("Nạp thẻ thành công")
                break
        if(not check):
            flash("Nạp thẻ thất bại")
    return render_template('napthe.html', bank=True)

@auth.route("/mbbank")
def mbbank():
    test = False
    while(not test):
        url = f"https://online.mbbank.com.vn/api/retail-web-transactionservice/transaction/getTransactionAccountHistory"
        time = datetime.now()
        today = time.strftime("%d/%m/%Y")
        yd = int((time.strftime("%d"))) - 1
        day = str(yd)
        if yd < 10:
            day = "0"+str(yd)
        yesterday = day + time.strftime("/%m/%Y")
        timenow = time.strftime("%Y%m%d%H%M%S") + "00"
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
        print(time.strftime("%Y/%m/%d %H:%M:%S"))
        if(data["result"]["message"] != "OK"):
            test = True
        else:
            timer.sleep(60)
    return data

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
    print(username, email, password, flush=True)
    user = User.query.filter_by(email=email).first()  # if this returns a user, then the email already exists in database

    if(session["captcha"] != cap):
        flash('Sai captcha')
        return redirect(url_for('auth.register'))
    
    if user:  # if a user is found, we want to redirect back to register page so user can try again
        flash('Email đã tồn tại')
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