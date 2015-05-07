import qiniu

access_key = 'FgXqyvkE-14bMEwmtYG-5-qqRppauVX5UvIMbJ8G'
secret_key = 'hG5oFakOvKw6Xlkz_HZPpu1xUQ5r-K0Xdcf8aWuG'
q = qiniu.Auth(access_key, secret_key)
token = q.upload_token('queue')
ret, info = qiniu.put_data(token, key, data)
if ret is not None:
    print('All is OK')
else:
    print(info) # error message in info
