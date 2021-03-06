﻿# python 中的协程和异步 

---
1. 函数加了yield关键字就变成了生成器。
2. 生成器是在**堆**上生成的，而我们普通的函数运行都是在栈上运行的，frame（栈帧)都是链表一样是相互有联系的，而生成器的frame是在堆上，完全自由，可以随便暂停开始，像云一样自由来去。
3. 通过`gen.gi_frame.f_locals`来获取生成器的内部变量值。
4. `next(),send()`用来启动生成器，在每个`yield`关键字处暂停并返回。此外还有`throw()`方法向生成器内部抛出错误。
5. 当生成器内部有这样的表达式时`left = yield right`，永远记得等号右边的`right`是生成器返回的的值，而等号左边的`left`接收`send(value)`的值，但不返回。
6. 协程是基于生成器这种可由程序员进行开始暂停结束的特点，主要是用到了**send**特性，可以将外部的数据传入到生成器的内部进行异步处理。python3.4之后把抽象的协程概念具体化了，变成语言特性的一种，通过装饰普通的生成器函数就成为协程。
7. 异步是指把事件抛出去，让它在一边玩，等到它完成了给个信号个主进程或者主线程通知事件完成了，然后运行相关的回调函数。
8. 事件循环就是一个调度异步事件的框架。
9. 两个关键，**Future**用来保存未来异步结果，而且执行相应的回调；**Task**驱动器，将需要驱动的生成器**封装**在内部，内部维护一个`run`方法用于不断向前驱动当前封装的生成器，值得注意的是这个`run`会被注册到`Future`回调方法里面，当异步结果发生并在保存结果的时，继续完成内部封装那个生成器。
