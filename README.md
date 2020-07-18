# Python压力测试工具
写这个东西的初衷是因为，马上就要压力测试，想要写一个工具并可以根据结果生成图表,在该项目基础上可以定制化开发

目前依然存在的问题创建大量线程时会有请求异常，暂时还没解决，后续会更新

用到的技术

 1. 多线程
 2. 锁
 3. requests
 4. pyecharts
 
 
 配置了两种发起请求方式(这里如果数量过多还可以再优化多线程循环)
 
 1. 快速请求，将请求池中的请求全部发送
 2. 慢速请求，在指定的时间内全部发送完毕
 ```python
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
 ```
 数据统计
 ```python
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
    # 打印成功请求的request中信息
    for success in sync.success:
        log.logger.debug(success.content)
    # 打印失败请求的request中信息
    for fail in sync.fail:
        if fail is not None:
            log.logger.debug(fail.content)
 ```
 多线程请求对象
 ```python
 class SyncRequestTask(threading.Thread):

    def __init__(self, threadId, url, method, params, header, timeout=10):
        threading.Thread.__init__(self)
        self.setName(f"sync-{threadId}")
        self.url = url
        self.method = method
        self.params = params
        self.timeout = timeout
        self.header = header

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
            print(e)
            fail.append(req)

    def doGet(self):
        startTime = time.time()

        s = sessions.session()
        req = s.get(self.url, headers=self.header, timeout=self.timeout)
        data_build(self.getName(), time.time() - startTime)
        req.close()
        return req

    def doPost(self):
        # request_body = json.dumps(self.params)
        s = sessions.session()
        startTime = time.time()
        req = s.post(self.url, data=self.params, headers=self.header, timeout=self.timeout)
        data_build(self.getName(), time.time() - startTime)
        req.close()
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
        # 开始发送请求
        self.request()
 ```

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200718122014667.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0RheV9EYXlfTm9fQnVn,size_16,color_FFFFFF,t_70)![在这里插入图片描述](https://img-blog.csdnimg.cn/20200718122039537.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0RheV9EYXlfTm9fQnVn,size_16,color_FFFFFF,t_70)