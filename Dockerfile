FROM python:3.9.16

RUN python3 -m pip install -i https://mirrors.aliyun.com/pypi/simple  --upgrade pip -i https://mirrors.aliyun.com/pypi/simple \
    && pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo 'Asia/Shanghai' >/etc/timezone


VOLUME /app/.env

WORKDIR /app

COPY ./guba_spider ./guba_spider
COPY ./scrapy.cfg ./scrapy.cfg
COPY ./main.py ./

CMD python3 main.py