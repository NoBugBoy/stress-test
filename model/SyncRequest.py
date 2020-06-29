import threading
import time
import json
import requests
from threading import Lock

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
lock = Lock()
success = []
fail = []
limit = 0
response_time = []
ids = []


def data_build(id, ms):
    print('ID {} 响应 {} ms'.format(id, ms))
    ids.append(id)
    response_time.append(ms)


class SyncRequestTask(threading.Thread):

    def __init__(self, threadId, url, method, params, timeout=3600):
        threading.Thread.__init__(self)
        self.id = threadId
        self.url = url
        self.method = method
        self.params = params
        self.timeout = timeout

    # 发送请求
    def request(self):
        req = None
        try:
            if self.method == 'GET':
                req = self.doGet()
                self.add(req)
            else:
                req = self.doPost()
                self.add(req)
        except Exception as e:
            fail.append(req)
            print(e)

    def doGet(self):
        req = requests.get(self.url, headers=headers, timeout=self.timeout)
        return req

    def doPost(self):
        request_body = json.dumps(self.params)
        req = requests.post(self.url, json=request_body, headers=headers, timeout=self.timeout)
        return req

    @staticmethod
    def add(request):
        global lock
        global limit
        lock.acquire()
        if request.status_code == 200:
            success.append(request)
        elif request.status_code == 429:
            limit += 1
        else:
            fail.append(request)
        lock.release()

    def run(self):
        startTime = time.time()
        # 开始发送请求
        self.request()
        # 传递参数，构建图标
        data_build(self.id, time.time() - startTime)
