import json
import os

class SortScrapSearch:
    def __init__(self, data_source=None) -> None:
        """
        Initialise le trieur de recherche d'appartements
        
        Args:
            data_source: Peut être un chemin vers un fichier JSON, 
                        un dictionnaire de données, ou None pour utiliser le fichier par défaut
        """
        self.search = self.getJson(data_source)
        self.rejectedSearch = {}
        self.validSearch = {}
        self.stats = {}
    
        self.sortSearch()
        self.calculateStats()
    
    def getJson(self, data_source=None):
        """
        Charge les données depuis différentes sources
        
        Args:
            data_source: Source des données (fichier, dictionnaire, ou None)
        """
        if isinstance(data_source, dict):
            # Si c'est déjà un dictionnaire, l'utiliser directement
            return data_source
        elif isinstance(data_source, str):
            # Si c'est un chemin de fichier
            if os.path.exists(data_source):
                with open(data_source, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                raise FileNotFoundError(f"Le fichier {data_source} n'existe pas")
        else:
            # Source par défaut
            default_files = ["./res.json", "./files/seLoger1.json"]
            for file_path in default_files:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        print(f"Données chargées depuis: {file_path}")
                        return data
            
            raise FileNotFoundError("Aucun fichier de données trouvé")
    
    def sortSearch(self):
        """
        Trie les annonces entre valides et rejetées selon les critères
        """
        for key, item in self.search.items():
            # Critères de rejet
            is_colocation = item.get("colocation", False)
            is_studio = item.get("studio", False)
            
            # Critères supplémentaires de validation
            has_valid_price = self.validatePrice(item.get("prix", ""))
            has_valid_surface = self.validateSurface(item.get("specificite", []))
            
            if not is_colocation and not is_studio and has_valid_price and has_valid_surface:
                self.validSearch[key] = item
                # Ajouter une note de validation
                item["validation_reason"] = "Critères respectés"
            else:
                self.rejectedSearch[key] = item
                # Ajouter la raison du rejet
                reasons = []
                if is_colocation:
                    reasons.append("colocation")
                if is_studio:
                    reasons.append("studio")
                if not has_valid_price:
                    reasons.append("prix invalide")
                if not has_valid_surface:
                    reasons.append("surface invalide")
                
                item["rejection_reason"] = ", ".join(reasons)
    
    def validatePrice(self, prix_str):
        """
        Valide si le prix est dans une fourchette acceptable
        
        Args:
            prix_str: Chaîne contenant le prix (ex: "550 €")
        
        Returns:
            bool: True si le prix est valide
        """
        if not prix_str or prix_str == "N/A":
            return False
        
        try:
            # Extraire le nombre du prix
            import re
            prix_match = re.search(r'(\d+)', prix_str.replace(" ", ""))
            if prix_match:
                prix = int(prix_match.group(1))
                # Fourchette de prix acceptable (peut être configurée)
                return 200 <= prix <= 800
        except:
            pass
        
        return False
    
    def validateSurface(self, specificites):
        """
        Valide si la surface est acceptable
        
        Args:
            specificites: Liste des spécificités de l'annonce
        
        Returns:
            bool: True si la surface est valide
        """
        import re
        for spec in specificites:
            if "m²" in spec:
                surface_match = re.search(r'(\d+)\s*m²', spec)
                if surface_match:
                    surface = int(surface_match.group(1))
                    # Surface minimale acceptable
                    return surface >= 30
        
        return False
    
    def calculateStats(self):
        """
        Calcule les statistiques sur les données
        """
        total = len(self.search)
        valid = len(self.validSearch)
        rejected = len(self.rejectedSearch)
        
        self.stats = {
            "total_annonces": total,
            "annonces_valides": valid,
            "annonces_rejetees": rejected,
            "taux_validation": round(valid / total * 100, 2) if total > 0 else 0,
            "prix_moyen_valides": self.calculateAveragePrice(self.validSearch),
            "surface_moyenne_valides": self.calculateAverageSurface(self.validSearch)
        }
    
    def calculateAveragePrice(self, data):
        """
        Calcule le prix moyen des annonces valides
        """
        import re
        prices = []
        for item in data.values():
            prix_str = item.get("prix", "")
            prix_match = re.search(r'(\d+)', prix_str.replace(" ", ""))
            if prix_match:
                prices.append(int(prix_match.group(1)))
        
        return round(sum(prices) / len(prices), 2) if prices else 0
    
    def calculateAverageSurface(self, data):
        """
        Calcule la surface moyenne des annonces valides
        """
        import re
        surfaces = []
        for item in data.values():
            specificites = item.get("specificite", [])
            for spec in specificites:
                if "m²" in spec:
                    surface_match = re.search(r'(\d+)\s*m²', spec)
                    if surface_match:
                        surfaces.append(int(surface_match.group(1)))
                        break
        
        return round(sum(surfaces) / len(surfaces), 2) if surfaces else 0
    
    def printStats(self):
        """
        Affiche les statistiques
        """
        print("\n" + "="*50)
        print("STATISTIQUES DE TRI")
        print("="*50)
        print(f"Total d'annonces analysées: {self.stats['total_annonces']}")
        print(f"Annonces valides: {self.stats['annonces_valides']}")
        print(f"Annonces rejetées: {self.stats['annonces_rejetees']}")
        print(f"Taux de validation: {self.stats['taux_validation']}%")
        print(f"Prix moyen (valides): {self.stats['prix_moyen_valides']} €")
        print(f"Surface moyenne (valides): {self.stats['surface_moyenne_valides']} m²")
        print("="*50 + "\n")
    
    def exportResults(self, filename="resultats_tries.json"):
        """
        Exporte les résultats triés
        
        Args:
            filename: Nom du fichier de sortie
        """
        results = {
            "statistiques": self.stats,
            "annonces_valides": self.validSearch,
            "annonces_rejetees": self.rejectedSearch,
            "metadata": {
                "date_traitement": __import__('datetime').datetime.now().isoformat(),
                "nombre_total": len(self.search)
            }
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Résultats exportés dans: {filename}")
    
    def getValidAnnouncements(self):
        """
        Retourne les annonces valides
        """
        return self.validSearch
    
    def getRejectedAnnouncements(self):
        """
        Retourne les annonces rejetées
        """
        return self.rejectedSearch
            
            
if __name__ == "__main__":
    SortScrapSearch()