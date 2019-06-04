# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import scrapy
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter
from scrapy.pipelines.images import ImagesPipeline


class WandoujiaPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonExportPipeline(object):
    def __init__(self, settings):
        self.save_file = open(os.path.join(settings.get("RESULT_PATH"), "Qu114.json"), "wb")
        self.exporter = JsonLinesItemExporter(self.save_file, encoding="utf8", ensure_ascii=False)
        self.exporter.start_exporting()

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.save_file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class QianLiYanSpiderPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        """
        处理对象，每一组item中图片的链接, 传递item对象，以便下一环节能使用
        :param item:
        :param info:
        :return:
        """
        for image_url in item['image_urls']:
            # 请求下载图片
            yield scrapy.Request(image_url, meta={'item': item})

    def file_path(self, request, response=None, info=None):
        """
        处理对象：每一张图片，返回的path 是item 中每一张图片的路径
        :param request:
        :param response:
        :param info:
        :return:
        """
        # 获取item中的联系人姓名作为图片的路径一部分
        image_name = request.meta['item']['contact']
        # 存储图片的路径
        path = 'full/' + image_name + '.jpg'
        return path

    def item_completed(self, results, item, info):
        """
        处理对象：每一组中的item中的图片
        :param results:
        :param item:
        :param info:
        :return:
        """
        # 图片的路径
        image_path = [x['path'] for ok, x in results if ok]

        if not image_path:
            raise DropItem("Item 中 不包含图片")
        item['image_paths'] = image_path
        return item


class JuHeBangSpiderPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        """
        处理对象，每一组item中图片的链接, 传递item对象，以便下一环节能使用
        :param item:
        :param info:
        :return:
        """
        for image_url in item['image_urls']:
            print("查看请求的图片连接：", image_url)
            # 请求下载图片
            yield scrapy.Request(image_url, meta={'item': item})

    # def file_path(self, request, response=None, info=None):
    #     """
    #     处理对象：每一张图片，返回的path 是item 中每一张图片的路径
    #     :param request:
    #     :param response:
    #     :param info:
    #     :return:
    #     """
    #     # 获取item中的联系人姓名作为图片的路径一部分
    #     image_name = request.meta['item']['phone']
    #     # 存储图片的路径
    #     path = 'full/' + image_name + '.jpg'
    #     return path

    def item_completed(self, results, item, info):
        """
        处理对象：每一组中的item中的图片
        :param results:
        :param item:
        :param info:
        :return:
        """
        # 图片的路径
        image_path = [x['path'] for ok, x in results if ok]

        if not image_path:
            raise DropItem("Item 中 不包含图片")
        item['image_paths'] = image_path
        return item
