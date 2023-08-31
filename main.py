from scrapy.cmdline import execute

execute('scrapy crawl eastmoney -s JOBDIR=.env/jobs'.split())
# execute('scrapy crawl eastmoney'.split())