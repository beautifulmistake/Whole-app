# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WandoujiaItem(scrapy.Item):
    # define the fields for your item here like:
    app_name = scrapy.Field()  # APP名称
    app_desc = scrapy.Field()  # 描述
    publish_time = scrapy.Field()  # 发布时间
    author = scrapy.Field()  # 开发者
    userDownloads = scrapy.Field()  # 下载次数
    img_url = scrapy.Field()  # APP图片地址
    detail_page = scrapy.Field()  # APP详情链接
    category = scrapy.Field()  # APP分类
    file_size = scrapy.Field()  # APP大小
    version = scrapy.Field()  # 版本号,需要去掉空格
    item_love = scrapy.Field()  # 用户好评
    comment_num = scrapy.Field()  # APP评论数
    app_inf = scrapy.Field()
    # APP 一级分类
    app_cate = scrapy.Field()
    # APP 二级分类
    app_category = scrapy.Field()
    # APP 三级分类
    app_sub_category = scrapy.Field()


class XiaoMiItem(scrapy.Item):
    # APP名称
    app_name = scrapy.Field()
    # APP 描述
    app_desc = scrapy.Field()
    # APP发布时间
    app_publishTime = scrapy.Field()
    # APP开发者
    app_author = scrapy.Field()
    # APP下载量
    app_downloads = scrapy.Field()
    # APP图片链接
    app_img = scrapy.Field()
    # APP详情页
    detail_page = scrapy.Field()
    # APP所属分类
    app_category = scrapy.Field()
    # APP大小
    app_fileSize = scrapy.Field()
    # APP版本号
    app_version = scrapy.Field()
    # APP评分
    app_comment = scrapy.Field()
    # APP评论次数
    app_commentNum = scrapy.Field()
    # APP 类别
    cate_name = scrapy.Field()


class SanLiuLing(scrapy.Item):
    # APP 名称
    app_name = scrapy.Field()
    # APP 所属一级分类
    cate_name = scrapy.Field()
    # APP 所属的二级分类
    category_name = scrapy.Field()
    # APP 应用介绍
    app_desc = scrapy.Field()
    # APP 基本信息
    app_info = scrapy.Field()


class HuaWei(scrapy.Item):
    app_name = scrapy.Field()
    app_desc = scrapy.Field()
    app_info = scrapy.Field()
    app_downloads = scrapy.Field()
    cate_name = scrapy.Field()
    category_name = scrapy.Field()


class KuaiDian8(scrapy.Item):
    search_title = scrapy.Field()
    info = scrapy.Field()


class QianLiYanItem(scrapy.Item):
    """
    本次的下载中包含图片的下载
    """
    # 搜索标题
    search_title = scrapy.Field()
    # 服务区域
    service_area = scrapy.Field()
    # 联系人
    contact = scrapy.Field()
    # 联系人手机（图片）
    images = scrapy.Field()     # 必要，不可自定义
    image_urls = scrapy.Field()     # 必要，不可自定义
    image_paths = scrapy.Field()  # 暂时还不太清楚具体的作用
    # 联系人QQ
    contact_qq = scrapy.Field()
    # 联系人邮箱
    contact_email = scrapy.Field()


class JinTiItem(scrapy.Item):
    # 搜索地区
    local = scrapy.Field()
    # 搜索标题
    search_title = scrapy.Field()
    # 搜索结果
    info = scrapy.Field()


class JuHeBangItem(scrapy.Item):
    # 搜索地区
    local = scrapy.Field()
    # 搜索类别
    cate_name = scrapy.Field()
    # 搜索标题
    search_title = scrapy.Field()
    # 地址
    address = scrapy.Field()
    # 联系人相关信息
    contact_info = scrapy.Field()
    # 手机号码
    phone = scrapy.Field()
    # 联系人手机（图片）
    images = scrapy.Field()  # 必要，不可自定义
    image_urls = scrapy.Field()  # 必要，不可自定义
    image_paths = scrapy.Field()  # 暂时还不太清楚具体的作用


class QiDianBaItem(scrapy.Item):
    # 搜索地区
    local = scrapy.Field()
    # 搜索类别
    cate_name = scrapy.Field()
    # 搜索标题
    search_title = scrapy.Field()
    # 所属区域
    sub_local = scrapy.Field()
    # 联系人信息
    info = scrapy.Field()


class Qu114Item(scrapy.Item):
    # 搜索地区
    local = scrapy.Field()
    # 搜索类别
    cate_name = scrapy.Field()
    # 搜索标题
    search_title = scrapy.Field()
    # 联系人信息
    info = scrapy.Field()
    # 手机号码
    contact = scrapy.Field()


