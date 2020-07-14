import model.SyncRequest as sync
import model.PrintPlt as plt
import time
import model.Logging as log
import model.ReadDatas as data
import json
import model.Utils as utils

# 请求池
syncPool = []
round_count = 1

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/83.0.4103.116 Safari/537.36',
    'Accept': 'application/json',
    'Connection': 'close',
    'Content-Type': 'application/json'
}


def init(count, url, methods='GET', params='{}', read=False):
    start_time = time.time()
    log.logger.info('开始预创建请求池....')
    if read:
        for requestId in range(count):
            dataList = data.request_data[requestId]
            if utils.check_json(str(dataList[0]).replace("'", "")):
                params = json.loads(str(dataList[0]).replace("'", ""))
            else:
                log.logger.error('json数据格式错误 跳过构建该请求')
                continue
            headers['openkey'] = dataList[1]
            request = sync.SyncRequestTask(requestId, url, methods, params, headers)
            syncPool.append(request)
    else:
        for requestId in range(count):
            request = sync.SyncRequestTask(requestId, url, methods, params, headers)
            syncPool.append(request)
    log.logger.info("初始化消耗时间 {:.2f} 豪秒".format((time.time() - start_time) * 1000))


# 这里id代表是第几次调用从0开始
def fast_run(begin, end):
    log.logger.warning("开始index{} 结束index{}".format(begin, end))
    run_start_time = time.time()
    log.logger.info('开始发起快速异步请求....')
    for request in syncPool[int(begin):int(end)]:
        request.start()
    log.logger.warning("请求消耗时间 {:.2f} 豪秒".format((time.time() - run_start_time) * 1000))


def slow_run(begin, end, slowTime):
    log.logger.warning("开始index{} 结束index{}".format(begin, end))
    run_start_time = time.time()
    log.logger.info('开始发起慢速异步请求....')
    if slowTime == 0:
        fast_run(begin, end)
    else:
        waitTime = round(((slowTime * 1000) / len(syncPool)) / 1000, 3)
        log.logger.info("延迟时间为{}毫秒".format(waitTime * 1000))
        for request in syncPool[int(begin):int(end)]:
            request.start()
            time.sleep(waitTime)
    log.logger.warning("请求消耗时间 {} 豪秒".format((time.time() - run_start_time) * 1000))


def join(begin, end):
    for request in syncPool[int(begin):int(end)]:
        request.join()


def out(length):
    log.logger.warning(f"总请求次数 {int(length)} 次")
    log.logger.warning(f"成功请求 {len(sync.success)} 次")
    log.logger.warning(f"失败请求 {len(sync.fail)} 次")
    log.logger.warning(f"限流请求 {sync.limit} 次")
    log.logger.warning("成功率 {:.2f} %".format((len(sync.success) / int(length)) * 100))
    log.logger.warning("失败率 {:.2f} %".format((len(sync.fail) / int(length)) * 100))
    log.logger.warning("限流百分比 {:.2f} %".format(sync.limit / int(length) * 100))
    log.logger.warning("最长请求时间 {:.2f} 毫秒".format(max(sync.response_time)))
    log.logger.warning("最短请求时间 {:.2f} 毫秒".format(min(sync.response_time)))
    log.logger.warning("平均请求时间 {:.2f} 毫秒".format(sum(sync.response_time) / len(sync.response_time)))
    # for success in sync.success:
    #     log.logger.debug(success.content)
    # for fail in sync.fail:
    #     if fail is not None:
    #         log.logger.debug(fail.content)


def switch_start(flag, slowTime, id):
    step = len(syncPool) / round_count
    begin = id * step
    if flag is True:
        fast_run(begin, begin + step)
    else:
        slow_run(begin, begin + step, slowTime)
    join(begin, begin + step)
    out(begin + step)
    generate_chart(id)
    # syncPool.clear()


def start(slowTime, roundCount, thread_count, request_url, method, param, read=False):
    log.logger.warning(f"共需要执行次数 {roundCount}")

    if roundCount > 1:
        global round_count
        round_count = roundCount

    init(thread_count * roundCount, request_url, str(method).upper(), param, read)
    if slowTime == 0:
        for count in range(roundCount):
            log.logger.warning(f"当前执行次数 {count + 1}")
            switch_start(True, 0, count)
    else:
        for count in range(roundCount):
            log.logger.warning(f"当前执行次数 {count + 1}")
            switch_start(False, slowTime, count)


def generate_chart(id):
    plt.show_bar(id)
    plt.show_pie(id)
