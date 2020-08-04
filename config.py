# -*- coding: UTF-8 -*-
from flask import Flask
import os


app = Flask(__name__)
ADMINS = ['larusx@163.com']
app.debug = True
if 'SERVER_SOFTWARE' not in os.environ:
    app.debug = True
if not app.debug:
    from gevent import monkey

    monkey.patch_all()
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler('smtp.sina.com',
                               'queuealert@sina.com',
                               ADMINS, 'YourApplication Failed',
                               ('queuealert@sina.com', 'queuealert'))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

app.secret_key = 'isc20z\a/r21a.b531sxj12'
app.jinja_env.variable_start_string = '{{ '
app.jinja_env.variable_end_string = ' }}'
initcontent = {'text':'推荐使用`Markdown`语法~', 'tag': 'Markdown'}
storage_address_data = "http://queue-battle.stor.sinaapp.com/"
