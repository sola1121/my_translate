http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#next-steps

*知识点*

+ 在你的应用中使用Celery
+ 调用任务们
+ 画布: 设计工作流
+ 路由
+ 远程控制
+ 时区
+ 优化

## Using Celery in your Application 在你的应用中使用Celery

### 我们的项目布局

    proj
      |-- __init__.py
      |-- celery.py
      |-- tasks.py

### proj/celery.py

    from __future__ import absolute_import, unicode_literals   # 针对py2引入的未来特性, 使用绝对路径导入, 使用Unicode编码的字符
    from celery import Celery

    app = ("proj",
            broker="",   # 这里设置所使用的broker的url
            backend="",  # 这里设置所使用的存储结果后端的url
            include=["proj.tasks"]
    )

    # 设置应用可选配置
    app.conf.update(result_expires=3600)   # 结果过期1小时

    if __name__ == "__main__":
        app.start()

在当前模块中, 你创建了我们的Celery实例. 要在你的项目中使用, 你只需要导入此实例即可.

后端用来保持对任务状态和结果的跟踪. 当结果被默认禁用时, 在这里我使用RPC结果存储后端, 因为我将演示如何检索结果. 你也可以使用不同的结果后端在你的应用中. 他们都有不同长处和短处. 如果你不需要结果, 那最好禁用他们. 结果也能在设置@task(ignore_result=True)的单个任务上被禁用.

include参数是一个当worker开始的时候被导入的模块的列表. 你需要在这儿添加我们的tasks模块, 这样worker可以找到我们的人物们.

### proj/tasks.py

    from __future__ import absolute_import, unicode_literals
    from .celery import app


    @app.task
    def add(x, y):
        return x + y


    @app.task
    def mul(x, y):
        return x * y


    @app.task
    def xsum(numbers):
        return sum(numbers):

### Starting the worker 开始项目的worker

在项目目录父目录上执行命令

    celery -A proj worker -l info

当开始一个worker后, 将会看到如下的内容

    -------------- celery@halcyon.local v4.0 (latentcall)
    ---- **** -----
    --- * ***  * -- [Configuration]
    -- * - **** --- . broker:      amqp://guest@localhost:5672//
    - ** ---------- . app:         __main__:0x1012d8590
    - ** ---------- . concurrency: 8 (processes)
    - ** ---------- . events:      OFF (enable -E to monitor this worker)
    - ** ----------
    - *** --- * --- [Queues]
    -- ******* ---- . celery:      exchange:celery(direct) binding:celery
    --- ***** -----

    [2012-06-08 16:23:51,078: WARNING/MainProcess] celery@halcyon.local has started.

_broker_ 是你在celery模块中指定broker的URL参数. 同时你也可以在命令行中通过-b选项指定不同的broker.

_concurrency_ 是prefork的worker的进程数量, 其被用来同时执行你的任务们, 当所有的这些都在处理工作流, 新的任务将会在队列中等待, 直到有空闲的进程再执行.  
默认的并发数是当前机器上CPU核心数量, 你可以通过`celery worker -c`选项自定义并发数. 没有推荐的值, 这依赖你的机器. 但是, 如果你的任务们大多数是I/O相关的, 你可以适当的增加并发数. 实验表明, 增加到你的核心数的两倍以上对性能的提升就很小了, 并很可能会降低执行性能.  
默认的是使用进程池, Celery同样也支持Eventlet, Gevent, 和跑在单线程上. http://docs.celeryproject.org/en/latest/userguide/concurrency/index.html#concurrency

_events_ 这是一个选项, 目的是让Celery对在worker中发生的活动发送监控消息(events). 这些可以被监测程序如celery events和Flower(celery的实时监控)使用.

_Queues_ 是一个worker消费的任务们的队列列表. worker能被告知消费同时消费几个队列, 这是被用在消息路由去指定workers作为一个服务质量, 分离的关注点, 优先级排序的手段. http://docs.celeryproject.org/en/latest/userguide/routing.html#guide-routing

### Stopping the worker 关闭工作流

可以直接在命令行中用键盘Control - c 关闭. 一系列的信号被worker支持.  可看 http://docs.celeryproject.org/en/latest/userguide/workers.html#guide-workers

### In the background 在后台
TODO: 
