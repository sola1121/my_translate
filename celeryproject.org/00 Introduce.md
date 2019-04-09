## What’s a Task Queue? 啥是任务队列

任务队列被用作一个通过线程或机器分配工作的分发机制.

一个任务队列的输入被叫做一个工作单元. 专用的worker进程不断监控任务队列以执行新工作.

Celery通过消息进行交流, 通常使用一个broker(中间件)来调节客户端和workers(工作流). 要开启一个任务, 客户端添加一个消息到队列中, 然后broker发送这个消息到worker.

## What do I need? 我需要啥

Celery需要一个消息处理中介来发送和接收消息. RabbitMQ和Redis的broker传输是功能齐全的, 但是也支持其他的实验性解决方案, 包括使用本地开发的SQLite.
