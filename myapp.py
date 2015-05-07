# -*- coding: UTF-8 -*-
from flask import render_template, request
import json
from design_redis import DataBase
import storage
from storage import Bucket
from used_functions import *
from config import *
import redis

import qiniu

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index2.html', username=session['username'].decode('utf-8'))
    else:
        return render_template('login.html')

@app.route('/begin')
def begin():
    return render_template('login.html')

@app.route('/token')
def token():
    access_key = 'FgXqyvkE-14bMEwmtYG-5-qqRppauVX5UvIMbJ8G'
    secret_key = 'hG5oFakOvKw6Xlkz_HZPpu1xUQ5r-K0Xdcf8aWuG'
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token('queue')
    ret = {}
    ret['uptoken'] = token
    return json.dumps(ret)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].encode('utf-8')
    if not username or username.find(' ') >= 0:
        return redirect(url_for('index'))
    password = request.form['password'].encode('utf-8')
    kv = DataBase(username)
    savedpassword = kv.get_user_password()
    if savedpassword and password == savedpassword:
        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login.html', wrongPassword=1)


@app.route('/chromeLogin', methods=['POST'])
def chromeLogin():
    username = request.form['username'].encode('utf-8')
    if not username or username.find(' ') >= 0:
        return '-1'
    password = request.form['password'].encode('utf-8')
    kv = DataBase(username)
    savedpassword = kv.get_user_password()
    if savedpassword and password == savedpassword:
        session['username'] = username
        return '0'
    return '-1'


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        session.pop('username', None)
    register_data = json.loads(request.data)
    if 'username' not in register_data or 'password' not in register_data:
        return '2'
    if register_data['username'] == '' or register_data['password'] == '':
        return '2'
    username = register_data['username'].encode('utf-8')
    password = register_data['password'].encode('utf-8')
    kv = DataBase(username)
    if kv.get_user_password():
        return '1'
    kv.add_new_user(username, password)
    content = []
    content.append(text_to_dict(json.dumps(initcontent)))
    kv.set_user_content(json.dumps(content))
    return '0'


@app.route('/history')
@login_required
def history():
    username = session['username']
    kv = DataBase(username)
    history = kv.get_user_history()
    if history is None:
        return 'No history'
    else:
        return render_template('history.html', history=history)


@app.route('/history/remove', methods=['POST'])
@login_required
def removeHistoryRecord():
    pass


@app.route('/upload', methods=['POST'])
@login_required
def upload():
    username = session['username']
    bucket = Bucket('battle')
    file = request.files['file']
    filename = file.filename.encode('utf-8')
    extname = filename.split('.')[-1]
    filename = hashlib.md5(filename).hexdigest()
    filedata = file.stream
    savename = username + '/' + filename + str(time.time()) + '.' + extname
    try:
        bucket.stat_object(savename)
        ret = storage_address_data + savename
    except storage.Error:
        bucket.put_object(savename, filedata)
        url = bucket.generate_url(savename)
        ret = url
    return ret


@app.route('/GetQueue')
@login_required
def GetQueue():
    username = session['username']
    kv = DataBase(username)
    return json.dumps(kv.get_user_content())


@app.route('/AddTodo', methods=['POST', 'GET'])
@login_required
def AddTodo():
    username = session['username']
    kv = DataBase(username)
    content = kv.get_user_content()
    data = text_to_dict(request.data)
    content.append(data)
    return kv.set_user_content(json.dumps(content))

@app.route('/deleteMark', methods=['POST'])
@login_required
def deleteMark():
    username = session['username']
    kv = DataBase(username)
    content = kv.get_user_content()
    hashcode = json.loads(request.data)['hash']
    for item in content:
        if item['hash'] == hashcode:
            content.remove(item)
            history = kv.get_user_history()
            history.append(item)
            kv.set_user_history(json.dumps(history))
            break
    return kv.set_user_content(json.dumps(content))



@app.route('/chromeAddTodo', methods=['POST'])
@login_required
def chromeAddTodo():
    username = session['username']
    kv = DataBase(username)
    content = kv.get_user_content()
    data = {'tag': request.form['tag'], 'text': request.form['text']}
    data = json.dumps(data)
    data = text_to_dict(data)
    content.append(data)
    kv.set_user_content(json.dumps(content))
    return '添加成功'


@app.route('/modifyTodo', methods=['POST'])
@login_required
def modifyTodo():
    username = session['username']
    kv = DataBase(username)
    content = kv.get_user_content()
    data = json.loads(request.data)
    for element in content:
        if element['hash'] == data['hash']:
            element['original'] = data['original']
            element['text'] = markdown_to_html(data['original'])
            element['tag'] = data['tag']
            break
    kv.set_user_content(json.dumps(content))
    return json.dumps(element)


@app.route('/SetQueue', methods=['POST', 'GET'])
@login_required
def SetQueue():
    username = session['username']
    data = json.loads(request.data)
    kv = DataBase(username)
    history = kv.get_user_history()
    ret = []
    for element in data:
        if element['done'] == True:
            history.append(element)
        else:
            ret.append(element)
    kv.set_user_history(json.dumps(history))
    return kv.set_user_content(json.dumps(ret))


# @app.route('/update_database')
# @admin_required
# def update():
#    kv = sae.kvdb.KVClient()
#    user = ['admin', 'xxxx', 'cc', 'll']
#    kv.set('user', json.dumps(user))


@app.route('/all_user')
@admin_required
def all_user():
    kv = DataBase()
    return json.dumps(kv.get_user_list(), ensure_ascii=False)


@app.route('/fake_user/<username>')
@admin_required
def fake_user(username=None):
    session['username'] = username.encode('utf-8')
    return redirect(url_for('index'))


@app.route('/reset_password', methods=['GET', 'POST'])
@admin_required
def reset_password():
    if request.method == 'GET':
        return render_template('resetpassword.html')
    register_data = json.loads(request.data)
    username = register_data['username'].encode('utf-8')
    password = register_data['password'].encode('utf-8')
    kv = DataBase(username)
    kv.set_user_password(password)
    return '0'


@app.route('/GetAnnouncement')
def GetAnnouncement():
    kv = DataBase()
    return kv.get_announcement()


@app.route('/SetAnnouncement')
@admin_required
def SetAnnouncement():
    kv = DataBase(session['username'])
    content = kv.get_user_content()
    for item in content:
        if item['tag'][0] == 'announcement':
            kv.set_announcement(item['text'])
            return 'OK'
    return 'None'


@app.route('/shareMark', methods=['POST'])
@login_required
def share_mark():
    username = session['username']
    hash_code = request.data
    kv = DataBase(username)
    content = kv.get_user_content()
    for item in content:
        if item['hash'] == hash_code:
            item['shareStatus'] = 1
            kv.operation_share_count(1)
            kv.set_user_content(json.dumps(content))
            break
    return '1'


@app.route('/vote', methods=['POST'])
@login_required
def vote():
    username = session['username']
    coding = Coding(username)
    return coding.vote()


@app.route('/unshareMark', methods=['POST'])
@login_required
def unshare_mark():
    username = session['username']
    hash_code = request.data
    kv = DataBase(username)
    content = kv.get_user_content()
    for item in content:
        if item['hash'] == hash_code:
            item['shareStatus'] = 0
            kv.operation_share_count(-1)
            kv.set_user_content(json.dumps(content))
            break
    return '0'


@app.route('/share/<username>', methods=['GET'])
def share_content(username):
    username = username.encode('utf-8')
    return render_template('share.html', username=username.decode('utf-8'))

@app.route('/getShareContent', methods=['POST'])
def getShareContent():
    username = request.data
    kv = DataBase(username)
    return json.dumps(kv.get_user_share_content())



@app.route('/share')
def share():
    kv = DataBase()
    users = []
    user_list = kv.get_user_list()
    for user in user_list:
        users.append({'name': user, 'count': kv.get_share_count(user)})
    return render_template('all_share.html', users=users)


@app.route('/login_coding')
@login_required
def login_coding():
    coding = Coding(session['username'])
    captcha = coding.get_captcha()
    response = app.make_response(captcha.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response

@app.route('/login_coding_home', methods=['GET', 'POST'])
def login_coding_home():
    coding = Coding(session['username'])
    current_status = coding.get_current_status()
    current_status = json.loads(current_status)
    if current_status['code'] == 1000:
        if_captcha_login = json.loads(coding.get_if_captacha_login())
        return render_template('login_coding.html', captcha=if_captcha_login['data'])
    if current_status['code'] == 0:
        return render_template('post_pp.html')

@app.route('/login_coding_with_captcha', methods=['POST'])
@login_required
def login_coding_with_captcha():
    username = request.form['username'].encode('utf-8')
    password = request.form['password'].encode('utf-8')
    if 'captcha' in request.form:
        captcha = request.form['captcha'].encode('utf-8')
    else:
        captcha = None
    coding = Coding(session['username'])
    return coding.login(username, password, captcha)

@app.route('/post_coding_pp', methods=['POST'])
@login_required
def post_coding_pp():
    coding = Coding(session['username'])
    text = request.data
    text_from = '\n\n{来自 [Yunmark](http://yunmark.coding.io/share/' + session['username'] + ')}'
    return coding.post_pp(text + text_from)

@app.route('/get_receive_box')
@login_required
def get_receive_box():
    username = session['username']
    kv = DataBase(username)
    receive_content = kv.get_receive_content(username)
    return json.dumps(receive_content)


@app.route('/get_user_list')
@login_required
def get_user_list():
    kv = DataBase()
    return json.dumps(kv.get_user_list())

@app.route('/send_mark', methods=['POST'])
@login_required
def send_mark():
    kv = DataBase()
    data = json.loads(request.data)
    content_dict = text_to_dict(request.data)
    content_dict['from'] = session['username']
    kv.send_to_user(data['username'], content_dict)
    return '0'

@app.route('/remove_from_receive_box', methods=['POST'])
@login_required
def remove_from_receive_box():
    username = session['username']
    hash = json.loads(request.data)
    hash = hash['hash']
    kv = DataBase(username)
    receive_content = kv.get_receive_content(username)
    for item in receive_content:
        if isinstance(item, dict) and 'hash' in item and item['hash'] == hash:
            receive_content.remove(item)
            kv.set_receive_content(username, receive_content)
            return '0'
    return '0'


@app.route('/transfer_from_tk', methods=['POST'])
def transfer_from_tk():
    username = request.form['username'].encode('utf-8')
    data = request.form['data'].encode('utf-8')
    if data == '[]':
        return '-1'
    kv = DataBase(username)
    data = json.loads(data)
    ret = kv.get_user_content()
    ret.extend(data)
    return kv.set_user_content(json.dumps(ret))



if __name__ == "__main__":
    # os.environ['sae.storage.path'] = './storage'
    # os.environ['HTTP_HOST'] = 'queue'
    # os.environ['debug'] = 'local'
    app.run('0.0.0.0', port=3000)