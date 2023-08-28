# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GubaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class EastMoneyPostItem(scrapy.Item):
    """
    股吧帖子基本信息
    """


    post_id = scrapy.Field()
    post_title = scrapy.Field()
    stockbar_code = scrapy.Field()
    stockbar_name = scrapy.Field()
    stockbar_type = scrapy.Field()
    user_id = scrapy.Field()
    user_nickname = scrapy.Field()
    user_extendinfos = scrapy.Field()
    post_click_count = scrapy.Field()
    post_forward_count = scrapy.Field()
    post_comment_count = scrapy.Field()
    post_publish_time = scrapy.Field()
    post_last_time = scrapy.Field()
    post_type = scrapy.Field()
    post_state = scrapy.Field()
    post_from_num = scrapy.Field()
    v_user_code = scrapy.Field()
    post_top_status = scrapy.Field()
    post_has_pic = scrapy.Field()
    post_has_video = scrapy.Field()
    user_is_majia = scrapy.Field()
    post_ip = scrapy.Field()
    qa = scrapy.Field()
    grade_type = scrapy.Field()
    institution = scrapy.Field()
    notice_type = scrapy.Field()
    post_display_time = scrapy.Field()
    media_type = scrapy.Field()
    zmt_article = scrapy.Field()
    post_source_id = scrapy.Field()
    bullish_bearish = scrapy.Field()
    modules = scrapy.Field()
    spec_column = scrapy.Field()
    cms_media_type = scrapy.Field()
    art_unique_url = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class EastmoneyCommentItem(scrapy.Item):

    child_replys = scrapy.Field()
    fake_child_replys = scrapy.Field()
    reply_count = scrapy.Field()
    child_reply_count = scrapy.Field()
    reply_id = scrapy.Field()
    source_post_code = scrapy.Field()
    source_post_id = scrapy.Field()
    reply_state = scrapy.Field()
    user_id = scrapy.Field()
    reply_time = scrapy.Field()
    reply_publish_time = scrapy.Field()
    reply_text = scrapy.Field()
    reply_picture = scrapy.Field()
    reply_is_top = scrapy.Field()
    reply_like_count = scrapy.Field()
    reply_is_like = scrapy.Field()
    reply_is_author = scrapy.Field()
    reply_is_amazing = scrapy.Field()
    reply_is_follow = scrapy.Field()
    reply_user = scrapy.Field()
    reply_ar = scrapy.Field()
    reply_from = scrapy.Field()
    reply_ip_address = scrapy.Field()
    reply_hide = scrapy.Field()
    reply_extend = scrapy.Field()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class EastmoneySpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stockname = scrapy.Field()
    home_page = scrapy.Field()
    forward = scrapy.Field()
    comment = scrapy.Field()
    article_url = scrapy.Field()
    author = scrapy.Field()
    fb_date = scrapy.Field()
    fb_time = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()