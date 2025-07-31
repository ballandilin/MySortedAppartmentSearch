import scrapy
from scrapy.crawler import CrawlerProcess
import json
import re
import os
from datetime import datetime


class ImmoScrap(scrapy.Spider):
    name = "ImmoScrap"
    start_urls = [
        'https://www.seloger.com/list.htm?projects=1&types=2,1&places=[{"inseeCodes":[210292]},{"inseeCodes":[210231]}]&price=NaN/550&surface=40/NaN&rooms=2,3&mandatorycommodities=0&enterprise=0&qsVersion=1.0&sort=d_dt_crea&m=search_hp_last'
    ]
    
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,  # Délai entre les requêtes
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 1,
        'COOKIES_ENABLED': True,
    }
    
    def __init__(self, *args, **kwargs):
        super(ImmoScrap, self).__init__(*args, **kwargs)
        self.results = {}
        self.page_count = 0
        self.max_pages = 5  # Limiter le nombre de pages
    
    def contains_word(self, s, words):
        """
        Vérifie si la chaîne contient un des mots de la liste
        
        Args:
            s: Chaîne à vérifier
            words: Liste de mots à rechercher
        
        Returns:
            bool: True si un mot est trouvé
        """
        if not s:
            return False
        
        s_lower = s.lower()
        return any(word.lower() in s_lower for word in words)
    
    def extract_surface(self, specificites):
        """
        Extrait la surface depuis les spécificités
        
        Args:
            specificites: Liste des spécificités
        
        Returns:
            int: Surface en m² ou None
        """
        for spec in specificites:
            if "m²" in spec:
                match = re.search(r'(\d+)\s*m²', spec)
                if match:
                    return int(match.group(1))
        return None
    
    def extract_rooms(self, specificites):
        """
        Extrait le nombre de pièces depuis les spécificités
        
        Args:
            specificites: Liste des spécificités
        
        Returns:
            int: Nombre de pièces ou None
        """
        for spec in specificites:
            if "pièce" in spec:
                match = re.search(r'(\d+)\s*pièce', spec)
                if match:
                    return int(match.group(1))
        return None
    
    def clean_price(self, prix_str):
        """
        Nettoie et standardise le prix
        
        Args:
            prix_str: Chaîne contenant le prix
        
        Returns:
            str: Prix nettoyé
        """
        if not prix_str:
            return "N/A"
        
        # Supprimer les espaces en trop et standardiser
        prix_clean = prix_str.strip()
        if not prix_clean or prix_clean == "":
            return "N/A"
        
        return prix_clean
    
    def parse(self, response):
        """
        Parse la page de résultats SeLoger
        """
        self.page_count += 1
        self.logger.info(f"Scraping page {self.page_count}")
        
        articles = response.css('div[data-testid="sl.explore.card-container"]')
        
        if not articles:
            self.logger.warning(f"Aucun article trouvé sur la page {self.page_count}")
            return
        
        for i, article in enumerate(articles):
            # Extraction des données de base
            lien_relatif = article.css("a[data-testid='sl.explore.coveringLink']::attr(href)").get()
            lien = "https://www.seloger.com" + lien_relatif if lien_relatif else None
            
            type_bien = article.css("div[data-test='sl.title']::text").get()
            if not type_bien:
                type_bien = article.css("div[data-test='sl.title'] *::text").get()
            
            prix_brut = article.css("div[data-test='sl.price-label']::text").get()
            prix = self.clean_price(prix_brut)
            
            description = article.css("div[data-testid='sl.explore.card-description']::text").get()
            if not description:
                description = ""
            
            localisation = article.css("div[data-testid='sl.address']::text").get()
            if not localisation:
                localisation = article.css("div[data-testid='sl.address'] *::text").get()
            
            # Spécificités (surface, pièces, étage, etc.)
            specificite = []
            specs_elements = article.css("li::text").getall()
            for spec in specs_elements:
                if spec and spec.strip():
                    specificite.append(spec.strip())
            
            # Détection des types de logement à éviter
            colocation_keywords = ["colocation", "coloc", "Colocation", "Coloc", "colocataire"]
            studio_keywords = ["studio", "Studio", "STUDIO"]
            
            colocation = self.contains_word(description, colocation_keywords)
            studio = self.contains_word(description, studio_keywords) or self.contains_word(type_bien, studio_keywords)
            
            # Extraction de données numériques
            surface = self.extract_surface(specificite)
            nombre_pieces = self.extract_rooms(specificite)
            
            # Génération d'un ID unique
            article_id = f"page{self.page_count}_item{i}"
            
            # Construction de l'objet annonce
            annonce = {
                'id': article_id,
                'lien': lien,
                'type': type_bien or "N/A",
                'prix': prix,
                'localisation': localisation or "N/A",
                'specificite': specificite,
                'description': description,
                'surface_m2': surface,
                'nombre_pieces': nombre_pieces,
                'colocation': colocation,
                'studio': studio,
                'date_scraping': datetime.now().isoformat(),
                'VALIDE': None  # Sera déterminé par le tri
            }
            
            self.results[article_id] = annonce
        
        # Sauvegarde intermédiaire
        self.save_results()
        
        # Gestion de la pagination
        next_page = response.css('a.next::attr(href)').get()
        if next_page and self.page_count < self.max_pages:
            self.logger.info(f"Passage à la page suivante: {self.page_count + 1}")
            yield response.follow(next_page, self.parse)
        else:
            if self.page_count >= self.max_pages:
                self.logger.info(f"Limite de {self.max_pages} pages atteinte")
            else:
                self.logger.info("Aucune page suivante trouvée")
            
            # Sauvegarde finale
            self.save_results(final=True)
    
    def save_results(self, final=False):
        """
        Sauvegarde les résultats dans un fichier JSON
        
        Args:
            final: Si True, sauvegarde finale avec métadonnées
        """
        if final:
            # Sauvegarde avec métadonnées
            final_results = {
                'metadata': {
                    'date_scraping': datetime.now().isoformat(),
                    'nombre_annonces': len(self.results),
                    'pages_scrapees': self.page_count,
                    'url_base': self.start_urls[0] if self.start_urls else None
                },
                'annonces': self.results
            }
            
            with open("res_detailed.json", "w", encoding="utf-8") as f:
                json.dump(final_results, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Sauvegarde finale: {len(self.results)} annonces dans res_detailed.json")
        
        # Sauvegarde simple pour compatibilité
        with open("res.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Sauvegarde: {len(self.results)} annonces")

def run_scraper(max_pages=5, output_file="res.json"):
    """
    Lance le scraper de manière indépendante
    
    Args:
        max_pages: Nombre maximum de pages à scraper
        output_file: Fichier de sortie
    
    Returns:
        dict: Données scrapées ou None en cas d'erreur
    """
    try:
        # Configuration du processus
        process = CrawlerProcess(settings={
            'LOG_LEVEL': 'INFO',
            'FEEDS': {
                output_file: {
                    'format': 'json',
                    'encoding': 'utf8',
                    'overwrite': True,
                },
            },
        })
        
        # Lancement du spider
        spider = ImmoScrap
        spider.max_pages = max_pages
        
        process.crawl(spider)
        process.start()
        
        # Retourner les données si le fichier existe
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
        
    except Exception as e:
        print(f"Erreur lors du scraping: {e}")
        return None

if __name__ == "__main__":
    # Configuration de la journalisation pour afficher les résultats.
    process = CrawlerProcess(settings={
        'LOG_LEVEL': 'DEBUG',  # Définissez le niveau de journalisation sur DEBUG.
    })
    
    process.crawl(ImmoScrap)
    process.start()
