# -*- coding: UTF-8 -*-
from functools import wraps
import re
import StringIO
from flask import session, redirect, url_for
import time
import misaka as m
import hashlib
import json
import urllib2
import urllib
import cookielib
from design_redis import DataBase


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] != 'admin':
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


def waste_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        func = f(*args, **kwargs)
        print 'Waste time : %s \n' % (time.time() - start_time)
        return func

    return decorated_function


def waster_time_args(arg):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            print arg
            rv = f(*args, **kwargs)
            print arg
            return rv

        return decorated_function

    return decorator


def text_to_dict(text, hash=None):
    text_dict = json.loads(text)
    text = text_dict.get('text', '')
    tag = []
    tags = text_dict.get('tag', '')
    tags = re.sub(r'\s+', ' ', tags.strip())
    tag.extend(tags.split(' '))
    data = dict()
    data['text'] = markdown_to_html(text)
    data['original'] = text
    data['done'] = False
    if hash == None:
        data['hash'] = str(hashlib.md5(text.encode('utf-8')).hexdigest() + str(time.time())).split('.')[0]
    else:
        data['hash'] = hash
    data['tag'] = tag
    data['shareStatus'] = 0
    return data


class BleepRenderer(m.HtmlRenderer, m.SmartyPants):
    def postprocess(self, text):
        return re.subn(r'<a', r'<a target="_blank"', text)[0]
        return text.replace(' ', '_')


def markdown_to_html(text):
    renderer = BleepRenderer()
    md = m.Markdown(renderer, extensions=m.EXT_FENCED_CODE | m.EXT_STRIKETHROUGH | m.HTML_HARD_WRAP)
    return md.render(text)

class Coding(object):
    home_url = 'https://coding.net/home.html'
    login_url = 'https://coding.net/api/login'
    post_pp_url = 'https://coding.net/api/tweet'
    relation_url = 'https://coding.net/api/user/relationships/all'
    current_user_url = 'https://coding.net/api/current_user'
    captcha_url = 'https://coding.net/api/getCaptcha'
    captcha_login_url = 'https://coding.net/api/captcha/login'
    vote_url = 'https://coding.net/api/marketing/html5/competition/vote/59'
    def __init__(self, username):
        self.username = username
        # 实例化一个全局opener
        self.opener = urllib2.build_opener()
        self.kv = DataBase(username)

    def login(self, username, password, captcha=None):
        cookie = self.kv.get_coding_cookie_key()
        data = {
            'email': username,
            'password': password,
        }
        if captcha is not None:
            data['captcha'] = captcha
        headers = {
            'Cookie': cookie
        }
        req = urllib2.Request(self.login_url, urllib.urlencode(data), headers=headers)
        result = self.opener.open(req)
        if 'set-cookie' in result.headers:
            self.kv.set_coding_cookie_key(result.headers['set-cookie'].split(';')[0])
        return result.read()


    def get_current_status(self):
        headers = {
            'Cookie': self.kv.get_coding_cookie_key(),
            'Referer': 'https://coding.net/login'
        }
        req = urllib2.Request(self.current_user_url, headers=headers)
        result = self.opener.open(req)
        if 'set-cookie' in result.headers:
            self.kv.set_coding_cookie_key(result.headers['set-cookie'].split(';')[0])
        return result.read()

    def get_if_captacha_login(self):
        #获取验证码
        headers = {
            'Cookie': self.kv.get_coding_cookie_key(),
            'Referer': 'https://coding.net/login'
        }
        req = urllib2.Request(self.captcha_login_url, headers=headers)
        result = self.opener.open(req)
        if 'set-cookie' in result.headers:
            self.kv.set_coding_cookie_key(result.headers['set-cookie'].split(';')[0])
        return result.read()

    def get_captcha(self):
        #获取验证码
        headers = {
            'Cookie': self.kv.get_coding_cookie_key(),
            'Referer': 'https://coding.net/login'
        }
        req = urllib2.Request(self.captcha_url, headers=headers)
        result = self.opener.open(req)
        if 'set-cookie' in result.headers:
            self.kv.set_coding_cookie_key(result.headers['set-cookie'].split(';')[0])
        return StringIO.StringIO(result.read())

    def post_pp(self, text):
        data = {
            'content': text
        }
        headers = {
            'Cookie': self.kv.get_coding_cookie_key()
        }
        data = urllib.urlencode(data)
        req = urllib2.Request(self.post_pp_url, data, headers)
        result = self.opener.open(req)
        return result.read()

    def vote(self):
        headers = {
            'Cookie': self.kv.get_coding_cookie_key()
        }
        req = urllib2.Request(self.vote_url, data='yunmark', headers=headers)
        result = self.opener.open(req)
        return result.read()


