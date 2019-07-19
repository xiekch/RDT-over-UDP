# UDP实现可靠文件传输

author: xiekch

## 实验要求

1. 写一个文件传输程序 A，通过 UPD 来传输一个文件及其管理元数据（文件名、大小和日期等），在应用层处理报文出错、重组和乱序等问题，保证文件传输正确无误。


## 1.UDP实现可靠传输

可靠传输需要将文件按序无误的传输给对方，必须要解决三个问题：

1. 出错
2. 丢包
3. 乱序

本程序仿照TCP传输协议，对这三个问题进行了处理。实现了连续ARQ（Automatic Repeat-reQuest）协议。此外，还实现了拥塞控制和自适应的超时重传时间算法。

### 连续ARP协议

发送方采用流水线传输。流水线传输就是发送方可以连续发送多个分组，不必每发完一个分组就停下来等待对方确认。如下图所示：

![img](https://img-blog.csdn.net/20160313194725494)

通过使用**确认**和**超时**这两个机制，就可以在不可靠UDP服务的基础上实现可靠的信息传输。

### 出错

在UDP报文首部中，有2个字节长度的校验和，用来检测UDP用户数据报是否有错，有错就丢弃。而我们的数据包是以UDP为载体，故无需额外检测是否出错。

### 丢包

判断是否丢包有2个方法：

- 超时
- 3次对同一数据包的确认

处理算法：

- 采用累计确认算法，对按序到达的最后一个数据包发送确认
- 实现快速重传算法，只要有一个包确认达到三次，即立即重传。
- 选择重发。只重发发生丢包的数据包，节约网络带宽。

### 乱序

把没有按序到达的数据包先缓存下来，直到数据包有序排列，再交付给上层程序。

### 拥塞控制

实现慢启动、AIMD算法，分三种情况处理：

- 超时重发
  - 阈值设为原拥塞窗口的一半
  - 拥塞窗口设为1
- 3次重复确认重发
  - 阈值设为原拥塞窗口的一半
  - 拥塞窗口减半
- 未重发
  - 如果大于阈值，拥塞窗口加1
  - 否则，拥塞窗口翻倍

相关代码

```python
    def updataCongWin(self, resend, timeout):
        if resend == True:
            self.threshold = math.ceil(0.5*self.congWin)
            if timeout == True:
                self.congWin = 1
            else:
                self.congWin = self.threshold
        elif self.congWin < self.windowSize:
            if self.congWin >= self.threshold:
                self.congWin += 1
            else:
                self.congWin *= 2
```

### 自适应超时重传时间算法

采用自适应算法，分两种情况:

- 未重传

  timeout = 0.8 * timeout + 0.2 * rtt + 0.2 * rtt

- 重传

  timeout *= 2

相关代码

```python
    def updataTimeout(self, resend, rtt=1):
        if resend == True:
            if self.timeout < self.maxTimeout:
                self.timeout *= 2
        else:
            self.timeout = 0.8*self.timeout+0.2*rtt+0.2*rtt
```

### 程序流程

#### 发送方

1. 建立UDP socket
2. 打开文件，读取数据
3. 发送Syn=True数据包，建立连接
4. 发送文件管理元数据
5. 将在拥塞窗口内的文件数据发送出去
   1. 接收接收方确认
   2. 若发生丢包，重传数据包
   3. 更新拥塞窗口和超时重传时间
6. 重复4直至文件发送完毕
7. 发送Fin=True数据包，传输结束

#### 接收方

1. 建立UDP socket，绑定端口
2. 接收Syn=True数据包，开始接收文件
3. 接收文件管理元数据，输出并创建文件
4. 接收文件数据
   1. 若按序到达，发送确认
   2. 否则，缓存，发送确认
   3. 将有序数据写入文件
5. 重复4直接接收到Fin=True数据包，传输结束

### 实验结果

在跨越4个路由的情况下：传输130MB的压缩包文件，稳定的有效文件传输速率为600KB/s左右，丢包率为0.1%左右：

传输结束，压缩包可正常解压。

### 运行方式

```shell
python UDPClient.py [ServerIP] [ServerPort] [FileSavedDirectory]
```

```shell
python UDPServer.py [ServerIP] [ServerPort] [FileName]
```



### Todo

- 滑动窗口协议