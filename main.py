import model.SyncRequest as sync
import model.PrintPlt as plt
import time
import sys

syncPool = []


def init(count, url, methods='GET', params='{}'):
    print('开始预创建请求池....')
    for requestId in range(count):
        request = sync.SyncRequestTask(requestId, url, methods, params)
        syncPool.append(request)


def run():
    for request in syncPool:
        request.start()


def join():
    for request in syncPool:
        request.join()


def out():
    print(f"success count = {len(sync.success)} ")
    print(f"fail count = {len(sync.fail)} ")
    for success in sync.success:
        print(success.content)
    for fail in sync.fail:
        print(fail.status_code)


# python3 main.py 50 POST http://101.200.212.244/trade/api/artTopic/list/2

if __name__ == '__main__':
    thread_count = 50
    method = 'POST'
    param = '{}'
    request_url = 'http://101.200.212.244/trade/api/artTopic/list/2'
    if len(sys.argv) > 3:
        thread_count = int(sys.argv[1])
        method = str(sys.argv[2])
        request_url = str(sys.argv[3])
    else:
        print('参数错误')
        exit(1)

    init_start_time = time.time()
    init(thread_count, request_url, method, param)
    print("初始化消耗时间 {} ms".format(time.time() - init_start_time))
    run_start_time = time.time()
    run()
    print("请求消耗时间 {} ms".format(time.time() - run_start_time))
    join()
    out()
    plt.show()
