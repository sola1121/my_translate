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

    app = Celery("proj",
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

include参数是一个当worker开始的时候被导入的模块的列表. 你需要在这儿添加我们的tasks模块, 这样worker可以找到我们的任务们.

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

在生产环境中, 你将想要在后台运行worker, 更多  http://docs.celeryproject.org/en/latest/userguide/daemonizing.html#daemonizing

系统守护进程脚本使用celery multi 命令以在后台开始一个或多个workers

    celery multi start w1 -A proj -l info

重启如下

    celery multi restart w1 -A proj -l info

关闭如下

    celery multi stop w1 -A proj -l info

关闭命令是异步的所以其不会等待worker完全关闭. 你将可能想要使用stopwait命令来代替stop, stopwait将保证所有当前执行的任务在命令执行完毕前都将完全关闭.

*注意* celery multi不会保存worker的启动信息, 所以你需要使用相同的命令行参数在重启工作流的时候. 只有相同pidfile(进程文件)和logfile(日志文件)参数们必须在停止时被使用.

默认的, 其会创建pid和log文件在当前的目录, 以防范众多的workers在彼此之上启动, 你呗鼓励将这些文件放置在一个专用的目录中.

创建相应目录, 然后在运行celery multi的时候进行指定

    celery multi start w1 -A proj -l info --pidfile=/var/run/celery/%n.pid --logfile=/var/log/celery/%n%I.log

更多的启动命令  http://docs.celeryproject.org/en/latest/reference/celery.bin.multi.html#module-celery.bin.multi

    celery multi start 10 -A proj -l info -Q:1-3 images, video -Q:4,5 data -Q default -L:4,5 debug

### About the --app argument 关于--app参数

--app参数指定Celery应用(就是那个Celery实例)使用, 其必须以 _模块.路径:属性_ 的格式书写

但是当该参数尝试搜索应用实例的时候, 只有一个包名被赋予了这个参数, 这个参数也支持该快捷格式. 其会以下面的顺序取寻找所指定的包.  
`--app=proj`  
1. 一个叫 proj.app 的属性
2. 一个叫 proj.celery 的属性
3. 任何一个在proj模块中的Celery实例属性, 如果没有, 则开始在proj的子模块中寻找名为 proj.celery
4. 一个叫 proj.celery.app 的属性
5. 一个叫 proj.celery.celery 的属性
6. 任何一个在proj.celery模块中的Celery实例属性

## Calling Tasks 调用任务

你可以调用一个任务使用`delay()`方法, 也可以使用更底层的`apply_async()`方法  
接下来能让你指定执行选项, 比如运行时长(countdown), 队列应该被指定, 等等

    add.apply_async((2, 2), queue="lopri", countdown=10)

上面的例子, 任务将会被发送到一个名叫lopri的队列中, 而且这个任务在将此消息发出至少将执行10秒钟.

直接调用任务该任务将会在当前进程中执行, 所以没有任何消息被发送.

    add(2, 2)   # 直接执行而没有使用Celery

`delay()`, `apply_async()`和 applying(\_\_call__)这三方法代表了Celery调用API, 这也可以用于签名.  更多 http://docs.celeryproject.org/en/latest/userguide/calling.html#guide-calling

每一个任务的调用将会被给予一个唯一识别(一个UUID号), 这就是任务id.

delay和apply_async方法返回一个AsyncResult实例, 其可以用来保持对任务执行状态的追踪. 但是对于这个你需要指定并开启结果存储后端, 这样执行的状态就会被存储得到某个地方.

默认结果是被禁用的, 因为事实上其没有结果后端适合每一个应用, 所以根据各个后端的优缺点选择一个适合的. 对于大多数的任务保持返回值并不是有用的, 所以这是一个合理的默认处理. 也需要注意结果后端用来监控任务和workers不是有用的, 对于这个需求, Celery使用专门的事务消息 http://docs.celeryproject.org/en/latest/userguide/monitoring.html#guide-monitoring

如果你配置了一个结果后端, 你可以从一个任务中取回一个返回值

    res = add.delay(2, 2)
    res.get(timeout=1)

你可以查看任务的id通过id属性

    res.id

当任务抛出异常时, 你同样可以使用返回值来查看任务的traceback, 事实上默认result.get()将会传递任何的错误.

如果你不想要查看异常的traceback, 你可以使用propagate参数, 这样就不会产生traceback, 而是一串描述错误的字符

    res.get(propagate=False)

在这种情况下, 其将会返回异常实例以取代原先的, 检查任务的成功执行或者失败, 可以在返回实例上使用相应的方法

    res.failed()
    res.successful()

所以这个返回实例是怎么知道任务执行成功还是失败的呢? 其是通过产看任务的状态

    res.state

一个任务只能有一个状态, 但是会经理不同的阶段. 不同阶段的任务的状态如下

    PENDING -> STARTED ->SUCCESS

开始(started)状态是一个特殊的状态, 如果`task_track_started`设置启用的话, 其只被记录; 或者`@task(track_started=True)`选项被设置在了任务上.

等待(pending)状态是一个不被记录的状态, 但是任何未知的任务id都是该状态的, 可以通过如下例子

    from proj.celery import app
    res = app.AsyncResult("这是一个不存在的id")
    res.state   # 将会显示pending

如果任务被重试, 这个阶段能变得更加复杂. 当一个任务被重试了两次, 其状态将会如下

    PENDING -> STARTED -> RETRY -> STARTED -> RETRY -> STARTED -> SUCCESS

Calling tasks is described in detail in the http://docs.celeryproject.org/en/latest/userguide/calling.html#guide-calling

## Canvas: Designing Work-flows 设计工作流

你只需要学习如何使用已注册任务的delay方法调用一个任务, 但是有时候你可能想要传递任务调用的签名到别的进程中或者作为一个参数传递到另一个函数中. 对于此, Celery使用叫做signatures的.

一个签名(signature)包含单个任务调用的参数们和执行选项们在一个方法中, 这样就能被传递到函数或甚至序列化并发送.

你可以使用(2, 2)作为参数给add任务创建一个签名signature, 并倒计时10s

    add.signature((2, 2), countdown=10)

也可以使用快捷方式

    add.s(2, 2)

### And there's that calling API again ..  可以再次调用API

Signature实例也支持调用API: 这意味着他们有delay和apply_async方法.

但是这里有一点不同, signature也许已经指定了一个参数签名. add任务接收两个参数, 所以一个签名指定两个参数将生成一个完整的signature

    s1 = add.s(2, 2)
    res = s1.delay()
    res.get()

但是你同样可以制作一个不完整的signatures以生成partials

    # incomplete partial: add(?, 2)
    s2 = add.s(2)

s2现在是一个partial signature, 需要另外的参数以完成他. 这可以通过在一次执行signature来完成他.

    # resolves the partial: add(8, 2)
    res = s2.delay(8)
    res.get()

上面我们加上了参数8, 和原先的被推迟已经存在的参数2组成了完整的add(8, 2)的signature

关键字参数也能在之后被添上, 将会和已存在的关键字参数相合并, 但是新添加的参数会优先

    s3 = add.s(2, 2, debug=True)
    s3.delay(debug=False)   # 现在将debug改为了False

如上述signatures支持调用API: 意味着

+ sig.apply_async(args=(), kwargs={}, **options)

调用有可选的部分参数和部分关键字参数的signature. 也支持部分执行选项.

+ sig.delay(*args, **kwargs)

apply_async的开始参数版本. 任何参数将会先发制人到参数到signature中, 关键字参数被合并到任何已存在的键中.

所以所有这些看起来都挺有用的, 但是你能实际使用这些做什么? 接下来就需要介绍下canvas primitives...

### The Primitives 图元

group map chain starmap chord chunks  
这些原语本身就是签名对象, 所以他们之间能有不同的组合方式来实现复杂的工作流.

*注意* 这些示例检索结果, 所以为了能够运行这些示例, 你需要配置一个结果后端. 

#### Groups

一个group同时调用一系列的任务, 并返回一个专用的结果实例, 方便你以一个分组来检查结果, 也能按顺序拿到结果.

    from celery import group
    from proj.tasks import add

    group(add.s(i, i) for i in xrange(10)) ().get()

部分的分组

    g = group(add.s(i) for i in xrange(10))
    g(10).get()

#### Chains

任务可以被连接在一起, 这样一个任务的返回将可以依此的放入下一个任务作为参数执行.

    from celery import chain
    from proj.tasks import add, mul

    chian(add.s(4,4)) | mul.s(8)().get())   # (4+4)*8

或者一部分的链式

    g = chain(add.s(4) | mul.s(8))   # (?+4)*8
    g(4).get()

链亦可以被这样写

    (add.s(4,4) | mul.s(8)) ().get()

#### Chords

一个chord是一个带有回调的分组

    from celery import chord
    from proj.tasks import add, xsum

    chord( (add.s(i,i) for i in xrange(10)), xsum.s()) ().get()

一个链接到另一个任务的分组将会被自动转换为一个chord

    (group(add.s(i, i) for i in xrange(10)) | xsum.s()) ().get()

当这些图元都是signature类型的时候, 其可以被任意组合

    upload_document.s(file) | group(apply_filter.s() for filter in filters)

更多关于工作流 http://docs.celeryproject.org/en/latest/userguide/canvas.html#guide-canvas

## Routing 路由

Celery支持所有由AMQP提供的路由设备, 但是它也支持简单的向命名了的队列中发送消息的路由

task_routes设置通过名字使你能够路由任务并在一个地方集中管理

    app.conf.update(
        task_routes = {
            "proj.tasks.add": {"queue": "hipri"},
        },
    )

你也能在运行时指定apply_async的queue参数

    from proj.tasks import add
    add.apply_async((2,2), queue="hipri")

在之后你可以穿开启一个worker从指定的队列通过celery worker -Q选项

    celery -A proj worker -Q hipri

你可以通过使用一个逗号分割的列表指定多个队列. 比如你可以从默认的队列和hipri队列开启一个worker消费者, 在这里默认的队列叫做celery

    celery -A proj worker -Q hipri,celery

队列的顺序不影响worker中的权重

更多的路由, 包括完整的使用AMQP路由, http://docs.celeryproject.org/en/latest/userguide/routing.html#guide-routing

## Remote Control 远程控制

如果你正在使用RabbitMQ(AMQP), Redis或者Qpid作为broker, 你可以在运行时检查和控制worker.

查看worker正在运行的任务

    celery -A proj inspect active

该功能使用广播实现, 所以在cluster(簇)中的每一个worker都会收到远程控制的命令.

你也可以指定一个或多个worker来响应请求, 使用 `--destination`选项. 将会返回以逗号分割的worker主机的名字列表.

    celery -A proj inspect active --destination=celery@example.com

如果没有目的地, 每一个worker将会反应并回复请求.

`celery inspect`命令不包含改变worker中的任何东西的命令, 其将只会现在worker中发生的事信息和统计.

使用celery inspect --help获取获取更多关于检查命令的参数

`celery control`命令中包含能够在worker运行时改变其的命令

使用celery control --help获取更多关于控制的参数

当事件开始执行时, 你可以开始事件转存来看worker正在做的事儿.

    celery -A proj events --dump

或者你能开始curses接口

    celery -A proj events

当你完成监控, 你可以再一次取消事件

    celery -A proj control disable_events

`celery status`命令也使用远程控制命令和展示在cluster(簇)中并在线的worker的列表

    celery -A proj status

更多的celery命令和监控 http://docs.celeryproject.org/en/latest/userguide/monitoring.html#guide-monitoring

## Timezone 时区

内部和消息中的所有时间和日期都使用UTC时间.

当worker接收到一个消息, 比如, 有一个倒计时设置, 其会转换UTC时间到本地时间. 如果你想使用一个不同的时区而不是系统的, 你必须配置timezone设置

    app.conf.timezone = "Europe/London"

## Optimization 优化

默认的配置没有对于吞吐量的优化, 其会尝试在许多短任务和少量长任务上保持平衡, 一个在吞吐量和公平调度折中.

如果你有严格公平调度要求, 或想优化吞吐量, http://docs.celeryproject.org/en/latest/userguide/optimizing.html#guide-optimizing

如果你正在使用RabbitMQ, 你可以安装librabbitmq模块, 这是一个由C实现的AMQP客户端 https://pypi.org/project/librabbitmq/
