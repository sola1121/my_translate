http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#first-steps

*知识点*

+ 选择和安装一个消息传输器(broker)
+ 安装Celery并创建一个任务
+ 开始worker和调用任务
+ 在任务在不同状态下进行传输时保持追踪任务, 检查返回值

## Application 应用

使用Celery的第一件事就是创建一个Celery实例. 这个实例被用作所有使用Celery的入口点, 比如创建任务, 管理workers, 同时要保证其他模块可以导入他.

tasks.py

    from celery import Celery
    app = Celery("tasks", broker="pyamqp://guest@localhost//")

    @app.task
    def add(x, y):
        return x + y

`Celery`类的第一个参数是当前模块的名字. 只有在__main__模块中定义任务时才能自动生成名称.

第二个参数是broker关键字, 指定想使用的消息broker的URL地址. 这里使用的是RabbitMQ配置.

## Running the Celery worker server 运行Celery的worker服务

你现在可以通过执行我们的带worker参数的程序运行. 在命令行中

    celery -A tasks worker --loglevel=info

如果你想使用后台守护进程来运行worker. 可以使用你操作平台自带的工具, 或使用如supervisord的工具.

## Calling the task 调用任务

调用我们的任务可以使用`delay()`方法

这是`apply_async()`方法的一个快捷方式, 其给予了对任务执行的强力控制.

    from tasks import add
    add.delay(4, 4)

这个任务现在被刚才开启的worker执行. 你可以通过查看worker所在终端的输出核实.

调用一个任务将会返回一个`AsyncResult`实例. 这能被用于检查任务的状态, 等待任务的完成, 获取任务的返回值, 或者在任务执行失败后进行回调取错.

默认情况下不启用结果. 为了对远程的程序调用或保持在数据库中追踪任务的结果, 你将需要配置Celery以使用后端, 下面就将作介绍.

## Keeping results 保持结果

如果你想保持对tasks的状态的追踪, Celery需要存储或发送状态到某个地方. 这里有几个可以选择的内建的后端选项: SQLALchemy/Django ORM, Memcached, Redis, RPC(RabbitMQ/AMQP), 或者自己定义.

在下面这个例子中, 我们使用rpc结果后端, 其可以将返回的状态作为瞬态消息发送. 这个后端通过`Celery`类的`backend`参数指定(或者当你使用配置模块的时候通过`result_backend`设定)

    app = Celery("tasks", backend="rpc://", broker="pyamqp://")

或者如果你想使用Redis作为结果后端, 但是任使用RabbitMQ作为消息代理(broker) 这是一个流行的方案

    app = Celery("tasks", backend="redis://localhost", broker="pyampq://")

更多的结果后端配置 http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-result-backends

现在结果后端配置了, 让我们在调用一次任务. 这次将会在调用时得到作为返回的`AsyncResult`实例

    result = add.delay(4, 4)

`ready()`方法返回任务是否完成

    is_finished = result.ready()

可以等待result的完成, 但是这很少使用, 应为他将异步调用转换为了同步调用

    result.get(timeout=1)

如果结果抛出异常, `get()`竟会在一次抛出异常, 但是你可以通过指定`propagate`参数重载

    result.get(propagate=False)

如果任务抛出一个异常, 你也可以使用原始的trackback来获取

    result.traceback

_警告_ 后端会使用资源存储和发送结果. 为了保证这些资源使用后会释放, 你必须在每次调用任务返回`AsyncResult`实例后调用`get()`或`forget()`

## Configuration 配置

Celery, 就像一个消费者应用, 不需要过多的配置在操作上. 他有一个输入和输出. 输入必须连接到一个broker上, 输出能选择性的被连接到一个结果后端. 然而, 如果你仔细地看看返回, 一个成员中包含了载入的 滑块(sliders), 表盘(dials), 和按钮(bottons), 这就是配置.

默认的配置应该能足够的应对大多数使用的情景, 但是这有许多能让Celery更好工作的可选项. 了解更多 http://docs.celeryproject.org/en/latest/userguide/configuration.html#configuration

配置可以在app中直接设置或者通过使用专用的配置模块. 举个栗子, 你可以更改任务中默认的序列化工具(serializer)通过`task_serializer`配置

    app.conf.task_serializer = "json"

如果你需要一次性配置很多, 你可以使用`update`, 这个conf应该是个字典或者namedtuple之类的

    app.conf.update(
        task_serializer="json",
        accept_content=["json", "yaml"],   # 仅接收json和yaml
        result_serializer="josn",
        timezone="Asia/Shanghai",
        enable_utc=True
    )

对于大的项目, 推荐使用一个统一的配置. 不建议使用硬编码定期任务间隔和任务路由选项. 统一将这些放在一个地方是很棒的. 这对库是尤其友好的, 其可以让用户控制他们的任务行为. 一个集中式的配置将也允许你的系统管理员对系统的玛法做出调整.

你可以通过`app.config_from_object()`告诉Celery实例使用一个配置模块

    app.config_from_object("celeryconfig")   # 在这里这个模块名叫做celeryconfig

上面的例子, 一个叫做celeryconfig.py的模块必须在相同目录中被提供. 可以设置配置在其中

    broker_url = "pyamqp://"
    result_backend = "rpc://"

    task_serializer = "json"
    accept_content = ["json"]
    timezone = "Asia/Shanghai"
    enable_utc = True

为了保证配置模块没有问题, 可以通过Python -m 验证一次

    python -m celeryconfig

为了展示配置文件的强大功能, 您可以将行为不当的任务路由到专用队列

celeryconfig.py

    task_routes = {
        'tasks.add': 'low-priority',
    }

或者不使用路由方式, 你能设置限制任务的比率, 该类型的任务只有10个任务允许在一分钟内执行(10/m)

    task_annotations = {
        'tasks.add': {'rate_limit': '10/m'}
    }

如果你使用RabbitMQ或Redis作为broker, 你也能指定worker(工作流)来设置一个新的限制比率在任务执行的时候

    celery -A tasks control rate_limit tasks.add 10/m

任务路由 http://docs.celeryproject.org/en/latest/userguide/routing.html#guide-routing

