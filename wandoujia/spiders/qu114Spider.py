import json
from urllib.parse import urljoin
import scrapy
from wandoujia.items import Qu114Item


class Qu114Spider(scrapy.Spider):
    name = "Qu114"

    def start_requests(self):
        """
        读取QiDian8_city.json文件生成所有的url
        :return:
        """
        with open(r"G:\工作\APP\wandoujia\Qu114_city.json", 'r', encoding='utf-8') as f:
            data = f.readlines()
        # 遍历数据列表
        for d in data:
            # json 转换为字典
            d = json.loads(d)
            # 每一项都是一个字典：local-->url
            local = d.get('local')
            cate_name = d.get('cate_name')
            url = d.get('url')
            # 发起请求
            yield scrapy.Request(url=url, meta={"local": local, "cate_name": cate_name})

    def parse(self, response):
        """
        解析获取的页面
        :param response:
        :return:
        """
        # print('查看获取的响应：', response.text)
        if response.status == 200:
            # 获取当前的URL,切分URL，方便后期与页号部分拼接获取下一页的链接
            curr = "/".join(response.url.split("/")[:3])
            if "没有找到信息" not in response.text:
                # 下一页
                is_next = response.xpath('//ul[@class="list-pagination"]/li[last()]/descendant::text()').extract_first()
                # 获取详情页的链接
                detail_urls = response.xpath('//ul[@id="ctl00_DivInfoListControls"]/'
                                             'li/div/div[@class="media-body-title"]/a')
                for detail_url in detail_urls:
                    # 详情页的链接
                    url = detail_url.xpath('./@href').extract_first()
                    # 请求详情页
                    yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_detail)
                # 判断是否有下一页
                if is_next == "下一页":
                    # 获取下一页的连接
                    next_url = response.xpath('//ul[@class="list-pagination"]/li[last()]/a/@href').extract_first()
                    # 发起下一页的请求
                    yield scrapy.Request(url=urljoin(curr, next_url), meta=response.meta, callback=self.parse)

    def parse_detail(self, response):
        """
        解析详情页
        :param response:
        :return:
        """
        # print("查看获取的响应：", response.text)
        # 创建item
        item = Qu114Item()
        # 搜索地区
        local = response.meta['local']
        # 搜索类别
        cate_name = response.meta['cate_name']
        # 搜索标题
        search_title = response.xpath('//div[@class="viewad-title"]/h1/text()').extract_first()
        # 联系人信息列表
        info_list = response.xpath('//div[@class="viewad-meta2"]/div[position()>1]')
        # 列表存储标题
        title = list()
        # 列表存储信息
        text = list()
        for info in info_list:
            # 每一个都是一个 div/div 的结构
            title_ = "".join([x.strip() for x in info.xpath('./label/text()').extract()])
            title.append(title_)
            text_ = "".join([x.strip() for x in info.xpath('div/descendant-or-self::text()').extract()])
            text.append(text_)
        # 联系方式
        contact = response.xpath('//section[@class="viewad-contact"]/ul/li/a/text()').extract_first()
        item['local'] = local
        item['cate_name'] = cate_name
        item['search_title'] = search_title if search_title else "暂无"
        item['info'] = dict(zip(title, text))
        item['contact'] = contact if contact else "暂无"
        yield item
