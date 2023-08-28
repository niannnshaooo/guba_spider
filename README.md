# guba_spider
爬取东方财富股吧数据

数据直接通过东财股吧的接口进行调取，相比纯解析HTML内容更加精准丰富。

> 本项目仅做学习用途，投资有风险，入市需谨慎！！！

## python 环境

```shell
pip3 install virtualenv
virtualenv venv
source venv/bin/activate
```

## 代理
本项目采用了开源的代理池，[jhao104/proxy_pool](https://github.com/jhao104/proxy_pool)   
自行按照文档搭建服务之后，修改本项目的配置PROXY_SERVER_HOST 

## 数据保存
目前将帖子和评论通过中间件<code>ExportPipeline</code>保存到csv文件中，可以自行增加中间件进行保存
