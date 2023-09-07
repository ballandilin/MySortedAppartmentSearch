import scrapy


class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ['https://www.seloger.com/list.htm?projects=1&types=2,1&places=[{"inseeCodes":[210292]},{"inseeCodes":[210231]}]&price=NaN/550&surface=40/NaN&rooms=2,3&mandatorycommodities=0&enterprise=0&qsVersion=1.0&sort=d_dt_crea&m=search_hp_last']

    def parse(self, response):
        yield { 'response': response.body }
