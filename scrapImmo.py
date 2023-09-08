import scrapy
from scrapy.crawler import CrawlerProcess
import json

class ImmoScrap(scrapy.Spider):
    name = "ImmoScrap"
    start_urls = ['https://www.seloger.com/list.htm?projects=1&types=2,1&places=[{"inseeCodes":[210292]},{"inseeCodes":[210231]}]&price=NaN/550&surface=40/NaN&rooms=2,3&mandatorycommodities=0&enterprise=0&qsVersion=1.0&sort=d_dt_crea&m=search_hp_last']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'FEED_EXPORT_ENCODING' : 'utf-8'
    }
    
    
    def parse(self, response):
        items = {}
        for i, article in enumerate(response.css('div[data-testid="sl.explore.card-container"]')):
            lien = "https://www.seloger.com" + article.css("a[data-testid='sl.explore.coveringLink']::attr(href)").get()
            typeBien = article.css("div[data-test='sl.title']::text").get()
            prix = article.css("div[data-test='sl.price-label']::text").get()
            description = article.css("div[data-testid='sl.explore.card-description']::text").get()
            localisation = article.css("div[data-testid='sl.address']::text").get()
            specificite = [spe for spe in article.css("li::text").getall()]

            items[i] = {
                'lien': lien,
                'type' : typeBien,
                'prix': prix,
                'localisation' : localisation,
                'specificite' : specificite,
                'description' : description,
                'VALIDE' : None
            }
            
        with open("res.json", "w", encoding="utf-8") as f:
            json.dump(items, f)

        next_page = response.css('a.next::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

if __name__ == "__main__":
    # Configuration de la journalisation pour afficher les résultats.
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'DEBUG',  # Définissez le niveau de journalisation sur DEBUG.
    })
    
    process.crawl(ImmoScrap)
    process.start()
