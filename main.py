import model.SyncCore as sc
import model.Utils as util
import model.Logging as log
import model.ReadDatas as data
import time
import sys


def check_param(threadCount, requestUrl, methods, params):
    if threadCount <= 0:
        log.logger.error("请求数量不能小于 0 ")
        exit(0)
    if str(methods).lower() != 'get' and str(methods).lower() != 'post':
        log.logger.error("请求方法错误")
        exit(0)
    if util.check_url(requestUrl) is False:
        log.logger.error("请求地址格式错误")
        exit(0)
    if util.check_json(params) is False:
        log.logger.error("JSON格式错误")
        exit(0)


# python3 main.py 50 POST xx
if __name__ == '__main__':

    thread_count = 500
    method = 'POST'
    param = '{}'
    request_url = 'http://101.200.212.244/gateway/trade/api/art/preBuy'
    # # 多少秒执行完成 0代表并发
    slowTime = 0
    # url = ''
    # # 循环执行次数
    roundCount = 1
    # # 是否从文件读取数据
    read = False

    # if len(sys.argv) > 3:
    #     thread_count = int(sys.argv[1])
    #     method = str(sys.argv[2])
    #     request_url = str(sys.argv[3])
    #     if len(sys.argv) > 4:
    #         url = str(sys.argv[4])
    # else:
    #     print('参数数量错误')
    #     exit(1)
    # load数据

    startTime = time.time()

    # data.loadRequestData('/Users/xxx/Desktop/StressTestData-202007161112.txt')
    log.logger.info("读取数据消耗时间{}毫秒".format((time.time() - startTime) * 1000))
    check_param(thread_count - 1, request_url, method, param)
    sc.start(slowTime, roundCount, thread_count, request_url, method, param, read)
