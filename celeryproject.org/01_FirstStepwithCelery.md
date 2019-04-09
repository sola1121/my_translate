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

## Keeping results TODO: