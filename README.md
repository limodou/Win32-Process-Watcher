Win32-Process-Watcher
========================

## What's is?

它是一个用来在Windows平台上监控进程执行情况的service程序。因为我需要在Windows下
启动一些服务程序，并且希望如果这些程序出问题可以自动重启。在Linux下有一个很好的
工具是Supervisor，不过它不能用在Windows上，找了半天也没有和这个差不多的，所以就
自已写了一个简化版本，先够自已使用。所以功能和Supervisor比起来是非常简单。

## How does it works?

对进程运行监控目前由三部分组成：

* pywatcher.py 主要是实现了Service程序，可以注册到Windows的服务中，本身并不提供
  监控进程的功能，它会启动g_server.py程序。提供服务的启动、停止、安装到Service、
  从Service中删除等功能。
* g_server.py 提供了类似Supervisor的进程监控功能。进程可以配置在对应的watcher.ini
  中。它同时提供Sockek服务，用来处理客户端的请求。
* g_client.py 提供了客户端功能，可以用来显示进程状态、启动、停止及关闭功能。

整个监控在启动时:

1. 由pywatcher.py通过subprocess启动g_server.py程序
2. 由g_server.py根据watcher.ini启动相应的命令行
3. g_server.py会不断查看进程状态，如果有退出的进程，则自动重启
4. g_server.py同时接收命令行发过来的命令，根据命令对相应的进程进行控制

## 安装说明

* 安装python 2.7版本
* 安装pywin32包
* 安装geventlet 0.4.1包
* 安装gevent 1.0版本（现在只有rc版本）

本软件目前没有做成可安装版本，所以将下载后的代码解压到一个目录下直接运行即可。注意，
在运行前要先配置watcher.ini。

## 第一次配置

在运行前需要将包中带有的watcher.default.ini拷贝为watcher.ini。然后打开可以看到：

```
[server]
log_to = 'pywatcher.log'
host = '0.0.0.0'
post = 6001

#[program:uliweb]
#command = 'uliweb runserver --tornado'
#directory = 'Hello'
```

其中server用来定义g_sever.py要使用的socket的服务器地址和端口，一般可以保持缺省。
`log_to` 用来定义输出的日志文件。

下面注释的是应用程序，需要的话可以仿照这个来定义你自已的应用。分别说明一下：

* `[program:uliweb]` 用来定义应用程序的名字，冒号后面可以是不同的应用，可以通过这个
名字通过client来进行单独的控制。
* `command` 用来定义应用程序的执行命令行
* `directory` 用来定义应用程序执行时的路径
* `logfile` 缺省为 “应用名”.log。表示输出日志文件名。
* `logfile_maxbytes` 缺省为50M，单位目前是字节数。用来控制每个日志的大小。
* `logfile_backups` 缺省为10个。用来控制日志文件的个数。

## 服务设置

### 安装

在解压目录下运行：

```
python pywatcher.py install
```

这样就将服务进行了安装。

### 启动

```
python pywatcher.py start
```

### 停止

```
python pywatcher.py stop
```

### 删除

```
python pywatcher.py remove
```

## 客户端设置

服务设置主要是用来控制service的安装、删除与启停。但是本身并不用于更精细的控制。
所以更精细的控制要使用g_client.py来控制。目前提供以下命令：

### status

查看配置的进程运行状态

### start name

启动某个应用

### stop name

停目某个应用

## 调试

如果使用服务的方式在调试时比较麻烦，可以直接运行 g_server.py，如：

```
python g_server.py
```


