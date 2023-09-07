import scrapy
from scrapy.crawler import CrawlerProcess
import json

class ImmoScrap(scrapy.Spider):
    name = "ImmoScrap"
    start_urls = ['https://www.seloger.com/list.htm?projects=1&types=2,1&places=[{"inseeCodes":[210292]},{"inseeCodes":[210231]}]&price=NaN/550&surface=40/NaN&rooms=2,3&mandatorycommodities=0&enterprise=0&qsVersion=1.0&sort=d_dt_crea&m=search_hp_last']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }
    
        
    def parse(self, response):
        
        # res = {
        #     'response' : response.body,
        # }
        # with open("log.json", "w") as j:
        #     json.dump(res, j)
        yield { 'response': response.body }

if __name__ == "__main__":
    # Configuration de la journalisation pour afficher les résultats.
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'DEBUG',  # Définissez le niveau de journalisation sur DEBUG.
    })
    
    process.crawl(ImmoScrap)
    process.start()
