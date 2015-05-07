# -*- coding: UTF-8 -*-
import json
import sae.kvdb
from used_functions import text_to_dict


class DataBase(object):
    def __init__(self, username=''):
        self.share_content_key = username + '_share_content'
        self.share_hash_key = username + '_share_hash'
        self.kv = sae.kvdb.KVClient()
        self.username = username
        self.content_key = username + '_content'
        self.history_key = username + '_history'

    def get_user_list(self):
        return json.loads(self.kv.get('user'))

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
        if content is None or content == '':
            return []
        return json.loads(content)

    def get_user_share_content(self):
        content = self.get_user_content()
        share_content = []
        for item in content:
            if 'shareStatus' in item and item['shareStatus'] == 1:
                share_content.append(item['text'])
        if len(share_content) == 0:
            return None
        return share_content


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


if __name__ == '__main__':
    user_table = dict()
    user_table['user'] = list()
    user_list = user_table['user']
    user_list.append('wangxiulin')
    user_list.append('litianchen')
    print json.dumps(user_table, indent=4)