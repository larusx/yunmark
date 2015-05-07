# -*- coding: UTF-8 -*-
import urllib
import urllib2
import time


class Coding():
    def __init__(self):
        self.headers = {
            'Host': 'mlife.cmbchina.com',
            'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
            'User-Agent': 'cmblife 4.3.0 rv:430 (iPhone; iPhone OS 8.3; zh_CN)',
            'Accept-Encoding': 'gzip'
        }
        self.opener = urllib2.build_opener()

    def post_zhaoshang(self, content):
        data = {
            '_ver': '4.3.0',
            '_requuid': '9A5F9248-3B9F-4393-99B1-A0FAA9974EA0',
            '_pla': 'cmblife_iphone_4.3.0_',
            '_pro': 0,
            '_appId': '6FB45A56585F420C97436C091AD3E868',
            '_r': 'YES',
            '_iv': 27,
            '_id': '9A4675D4FCD64B3584C1ECF901B16F90',
            '_accountId': 'd3e20a93d4401db8783ae1e3639095d8',
            '_uid': 'd3e20a93d4401db8783ae1e3639095d8',
            'DeviceID': '9A4675D4FCD64B3584C1ECF901B16F90',
            'appId': '6FB45A56585F420C97436C091AD3E868',
            '_ss': '640*1136',
            '_mt': 'iphone6,2_8.3'
        }
        url = 'http://mlife.cmbchina.com/NeptuneApp/createOrderV2.json?'
        req = urllib2.Request(url + urllib.urlencode(data), data=urllib.urlencode(content), headers=self.headers)
        return self.opener.open(req).read()


if __name__ == '__main__':
    coding = Coding()
    content = {
        'accountId': 'd3e20a93d4401db8783ae1e3639095d8',
        'productId': '0060000001514',
        'mac': '295e198237d357cc0c8a94b9ed4d08a2',
        'orderAmount': 5600,
        'quantity': 1,
        'payType': 0
    }
    for i in xrange(0, 300):
        time.sleep(0.85)
        print coding.post_zhaoshang(content)
