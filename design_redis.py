# -*- coding: UTF-8 -*-
import json
import redis
import os


class DataBase(object):
    def __init__(self, username=''):
        self.share_content_key = username + '_share_content'
        self.share_hash_key = username + '_share_hash'
        if 'debug' not in os.environ:
            self.kv = redis.Redis(host=os.getenv('REDIS_PORT_6379_TCP_ADDR', 'localhost'),
                                  port=int(os.getenv('REDIS_PORT_6379_TCP_PORT', '6379')),
                                  db=0,
                                  password=os.getenv('REDIS_PASSWORD', ''))
        else:
            self.kv = redis.Redis(host='localhost', port=6379, db=0)
        self.username = username
        self.content_key = username + '_content'
        self.history_key = username + '_history'
        self.share_count_key = username + '_share_count'
        self.coding_cookie_key = username + '_coding_cookie'
        self.receive_key = username + '_receive_key'

    def send_to_user(self, username, text):
        receive_content = self.get_receive_content(username)
        receive_content.append(text)
        return self.kv.set(username + '_receive_key', json.dumps(receive_content))

    def get_receive_content(self, username):
        content = self.kv.get(username + '_receive_key')
        if content is None:
            return []
        return json.loads(content)

    def set_receive_content(self, username, content):
        return self.kv.set(username + '_receive_key', json.dumps(content))


    def get_coding_cookie_key(self):
        return self.kv.get(self.coding_cookie_key)

    def set_coding_cookie_key(self, key):
        return self.kv.set(self.coding_cookie_key, key)

    def get_user_list(self):
        ret = self.kv.get('user')
        if ret:
            return json.loads(self.kv.get('user'))
        else:
            return []

    def get_share_hash_list(self):
        share_hash_list = self.kv.get(self.share_hash_key)
        if share_hash_list is None or share_hash_list == '':
            return []
        return json.loads(share_hash_list)

    def set_share_hash_list(self, share_hash_list):
        self.kv.set(self.share_hash_key, share_hash_list)

    def set_user_list(self, user_list):
        self.kv.set('user', json.dumps(user_list))

    def get_user_password(self):
        return self.kv.get(self.username)

    def set_user_password(self, password):
        self.kv.set(self.username, password)

    def set_user_content(self, content):
        self.kv.set(self.content_key, content)
        return content

    def get_user_history(self):
        history = self.kv.get(self.history_key)
        if history is None or history == '':
            return []
        return json.loads(history)

    def set_user_history(self, history):
        self.kv.set(self.history_key, history)

    def get_user_content(self):
        content = self.kv.get(self.content_key)
        if content is None or content == '' or content == 'null':
            return []
        return json.loads(content)

    def get_user_share_content(self):
        content = self.get_user_content()
        share_content = []
        for index, item in enumerate(content):
            if 'shareStatus' in item and item['shareStatus'] == 1:
                share_content.append({'index': index, 'original': item['original'], 'text': item['text']})
        user_share_count = len(share_content)
        self.set_share_count(user_share_count)
        if user_share_count == 0:
            return None
        return share_content

    def set_share_count(self, count):
        return self.kv.set(self.share_count_key, count)

    def operation_share_count(self, op):
        key = self.kv.get(self.share_count_key)
        if key is None:
            self.kv.set(self.share_count_key, 1)
            return 0
        if op == 1:
            self.kv.set(self.share_count_key, str(int(key)+1))
        else:
            self.kv.set(self.share_count_key, str(int(key)-1))
        return 0

    def get_share_count(self, username):
        share_count_key = username + '_share_count'
        return self.kv.get(share_count_key)

    def get_announcement(self):
        return self.kv.get('announcement')

    def set_announcement(self, text):
        return self.kv.set('announcement', text)

    def add_new_user(self, username, password):
        self.username = username
        self.content_key = username + '_content'
        self.history_key = username + '_history'
        user_list = self.get_user_list()
        user_list.append(self.username)
        self.set_user_list(user_list)
        self.set_user_password(password)

