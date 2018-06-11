# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.item import Item, Field


class DiapersSizeInfoItem(Item):
    size_chart_type = Field()
    brand_name = Field()
    size_type = Field()
    size_info = Field()
    type = Field()


class ImageItem(Item):
    image = Field()
    thumbnail = Field()


class Color(Item):
    show_product_id = Field()
    from_site = Field()
    type = Field()
    cover = Field()
    cover_style = Field()
    images = Field()
    name = Field()
    version = Field()


class BaseItem(Item):
    type = Field()
    url = Field()
    title = Field()
    cover = Field()
    list_price = Field()
    current_price = Field()
    show_product_id = Field()
    desc = Field()
    colors = Field()  # 字符串数组
    sizes = Field()  # 改用dimensions
    dimensions = Field()  # 尺寸数组
    weight = Field()
    brand = Field()
    from_site = Field()
    product_type = Field()  # 增加了产品类型
    category = Field()
    sub_category = Field()
    '''gender的类型 baby toddler girls boys women men unisex kid-unisex'''
    gender = Field()  # 表示人群
    skus = Field()
    size_info = Field()
    begins = Field()
    ends = Field()
    size_country = Field()
    size_chart = Field()
    size_chart_pic = Field()
    dimension_names = Field()
    linkhaitao_url = Field()
    editor_flag = Field()
    product_type_id = Field()
    category_id = Field()
    groupbuy_num = Field()
    media_url = Field()
    related_items_id = Field()


class SkuItem(Item):
    type = Field()
    show_product_id = Field()
    from_site = Field()
    id = Field()
    list_price = Field()
    current_price = Field()
    color = Field()  # 颜色key，默认是default
    size = Field()
    is_outof_stock = Field()
    quantity = Field()
    s_t =Field()
    # size_num = Field()


class SaleBaseItem(BaseItem):
    begins = Field()
    ends = Field()
    sale_key = Field()
    is_sold_out = Field()
    good_json_url = Field()
    sale_keys = Field()


class SaleItem(Item):
    type = Field()
    from_site = Field()
    begins = Field()
    desc = Field()
    ends = Field()
    image_url = Field()
    name = Field()
    sale_json_url = Field()
    sale_key = Field()
    sale_url = Field()
    size = Field()
    store = Field()
    show_product_ids = Field()


class DistributeCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
