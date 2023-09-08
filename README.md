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
推荐采用阿布云代理，稳定更快
settings.py 中 中间件开启 阿布与代理

```python
DOWNLOADER_MIDDLEWARES = {
    # 在Setting.py 文件中找到下载器中间件 并解除注释
   'guba_spider.middlewares.RandomheaderDownloaderMiddleware': 543,
   'guba_spider.middlewares.ABYProxyMiddleware': 544,
   'guba_spider.middlewares.GubaRetryMiddleware': 550,
}
```

## 工作流程
* 股吧页的沪市和深市股票列表作为入口页提交爬取
* 每个股票的文章一页一页获取
  * 当前页可以知道总条数，按照一页80的条目计算分页数
  * 如果当前分页已经超出总的分页，则结束改股票的获取
* 每篇文章提交一个获取评论的请求（一次性获取全部）
* 数据通过管道保存到mongodb中
* 后续可以对mongodb中的数据进行处理和落盘到clickhouse中