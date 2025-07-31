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
                    data = json.load(f)
                    # Adapter le format si nécessaire
                    return self.normalizeDataFormat(data)
            else:
                raise FileNotFoundError(
                    f"Le fichier {data_source} n'existe pas")
        else:
            # Source par défaut
            default_files = ["./res.json", "./files/seLoger1.json"]
            for file_path in default_files:
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        print(f"Données chargées depuis: {file_path}")
                        return self.normalizeDataFormat(data)

            raise FileNotFoundError("Aucun fichier de données trouvé")

    def normalizeDataFormat(self, data):
        """
        Normalise le format des données pour qu'elles soient compatibles

        Args:
            data: Données brutes du fichier JSON

        Returns:
            dict: Données normalisées
        """
        normalized_data = {}

        for key, item in data.items():
            # Détecter le format des données
            if self.isSeLogerApiFormat(item):
                # Format API SeLoger (seLoger1.json)
                normalized_item = self.convertSeLogerApiFormat(item)
            elif self.isScrapedFormat(item):
                # Format scraped (res.json)
                normalized_item = item
            else:
                # Format inconnu, essayer de deviner
                normalized_item = self.guessFormat(item)

            if normalized_item:
                normalized_data[key] = normalized_item

        return normalized_data

    def isSeLogerApiFormat(self, item):
        """
        Vérifie si l'item est au format API SeLoger
        """
        return (
            isinstance(item, dict) and
            'object' in item and
            'annonce_id' in item and
            'description' in item
        )

    def isScrapedFormat(self, item):
        """
        Vérifie si l'item est au format scraped
        """
        return (
            isinstance(item, dict) and
            ('lien' in item or 'type' in item) and
            'prix' in item
        )

    def convertSeLogerApiFormat(self, item):
        """
        Convertit les données du format API SeLoger vers notre format standard
        """
        try:
            # Extraction des informations de base
            description = item.get('description', '')
            prix_str = f"{item.get('price', 0)} €" if item.get(
                'price') else "N/A"

            # Construction de l'URL
            annonce_id = item.get('annonce_id', '')
            lien = f"https://www.seloger.com/annonces/locations/appartement/{annonce_id}.htm" if annonce_id else ""

            # Type de bien
            type_bien = "Appartement"  # Par défaut
            if item.get('has_furnished'):
                type_bien = "Appartement meublé"

            # Localisation
            address = item.get('address', '')
            district = item.get('district', '')
            localisation = f"{address}, {district}" if district else address

            # Spécificités
            specificite = []

            # Nombre de pièces
            rooms = item.get('rooms_count', 0)
            if rooms:
                specificite.append(f"{rooms} pièces")

            # Nombre de chambres
            bedrooms = item.get('bedrooms_count', 0)
            if bedrooms:
                specificite.append(f"{bedrooms} chambres")

            # Surface
            area = item.get('area', 0)
            if area:
                specificite.append(f"{int(area)} m²")

            # Étage
            floor = item.get('floor', '')
            max_floor = item.get('max_floor', '')
            if floor and max_floor:
                specificite.append(f"Étage {floor}/{max_floor}")
            elif floor:
                specificite.append(f"Étage {floor}")

            # Équipements
            if item.get('has_balcony'):
                specificite.append("Balcon")
            if item.get('has_terrace'):
                specificite.append("Terrasse")
            if item.get('has_garden'):
                specificite.append("Jardin")
            if item.get('has_parking'):
                specificite.append("Parking")
            if item.get('has_elevator'):
                specificite.append("Ascenseur")

            # Détection colocation et studio
            colocation_keywords = [
                "colocation", "coloc", "Colocation", "Coloc", "colocataire", "colocation"]
            studio_keywords = ["studio", "Studio", "STUDIO"]

            colocation = self.contains_word(
                description, colocation_keywords) or rooms <= 1
            studio = self.contains_word(description, studio_keywords) or (
                rooms == 1 and bedrooms == 0)

            # Construction de l'objet normalisé
            normalized_item = {
                'lien': lien,
                'type': type_bien,
                'prix': prix_str,
                'localisation': localisation,
                'specificite': specificite,
                'description': description,
                'surface_m2': int(area) if area else None,
                'nombre_pieces': rooms if rooms else None,
                'colocation': colocation,
                'studio': studio,
                'VALIDE': None,
                # Données supplémentaires
                'annonce_id': annonce_id,
                'source': 'api_seloger'
            }

            return normalized_item

        except Exception as e:
            print(f"Erreur lors de la conversion de l'item: {e}")
            return None

    def guessFormat(self, item):
        """
        Essaie de deviner le format des données
        """
        # Format de base minimal
        return {
            'lien': item.get('lien', item.get('url', '')),
            'type': item.get('type', item.get('property_type', 'N/A')),
            'prix': item.get('prix', item.get('price', 'N/A')),
            'localisation': item.get('localisation', item.get('address', 'N/A')),
            'specificite': item.get('specificite', []),
            'description': item.get('description', ''),
            'colocation': item.get('colocation', False),
            'studio': item.get('studio', False),
            'VALIDE': None,
            'source': 'unknown'
        }

    def contains_word(self, text, words):
        """
        Vérifie si le texte contient un des mots de la liste
        """
        if not text:
            return False

        text_lower = text.lower()
        return any(word.lower() in text_lower for word in words)

    def sortSearch(self):
        """
        Trie les annonces entre valides et rejetées selon les critères
        """
        for key, item in self.search.items():
            # Critères de rejet
            is_colocation = item.get("colocation", False)
            is_studio = item.get("studio", False)

            # Critères supplémentaires de validation
            has_valid_price = self.validatePrice(
                item.get("prix", item.get("price", "")))
            has_valid_surface = self.validateSurfaceFromItem(item)

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
            prix_str: Chaîne contenant le prix (ex: "550 €") ou nombre

        Returns:
            bool: True si le prix est valide
        """
        if not prix_str or prix_str == "N/A":
            return False

        try:
            # Si c'est déjà un nombre
            if isinstance(prix_str, (int, float)):
                prix = float(prix_str)
            else:
                # Extraire le nombre du prix
                import re
                prix_match = re.search(
                    r'(\d+(?:\.\d+)?)', str(prix_str).replace(" ", "").replace(",", "."))
                if prix_match:
                    prix = float(prix_match.group(1))
                else:
                    return False

            # Fourchette de prix acceptable (peut être configurée)
            return 200 <= prix <= 1000  # Élargir la fourchette

        except Exception as e:
            print(f"Erreur validation prix '{prix_str}': {e}")
            return False

    def validateSurface(self, specificites):
        """
        Valide si la surface est acceptable

        Args:
            specificites: Liste des spécificités de l'annonce ou données directes

        Returns:
            bool: True si la surface est valide
        """
        import re

        # Si specificites est une liste
        if isinstance(specificites, list):
            for spec in specificites:
                if "m²" in str(spec):
                    surface_match = re.search(
                        r'(\d+(?:\.\d+)?)\s*m²', str(spec))
                    if surface_match:
                        surface = float(surface_match.group(1))
                        return surface >= 25  # Surface minimale acceptable

        # Si on a accès aux données directement dans l'item parent
        # (cette fonction sera appelée depuis sortSearch avec plus de contexte)
        return True  # Par défaut, accepter si pas d'info de surface

    def validateSurfaceFromItem(self, item):
        """
        Valide la surface depuis un item complet

        Args:
            item: Item complet avec toutes les données

        Returns:
            bool: True si la surface est valide
        """
        # Vérifier d'abord surface_m2 si disponible
        surface_m2 = item.get('surface_m2')
        if surface_m2 and isinstance(surface_m2, (int, float)):
            return surface_m2 >= 25

        # Sinon chercher dans les spécificités
        specificites = item.get('specificite', [])
        if isinstance(specificites, list):
            import re
            for spec in specificites:
                if "m²" in str(spec):
                    surface_match = re.search(
                        r'(\d+(?:\.\d+)?)\s*m²', str(spec))
                    if surface_match:
                        surface = float(surface_match.group(1))
                        return surface >= 25

        # Si aucune surface trouvée, vérifier dans les données brutes (format API)
        area = item.get('area')
        if area and isinstance(area, (int, float)):
            return area >= 25

        # Par défaut, accepter si pas d'information de surface
        return True

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
        print(
            f"Surface moyenne (valides): {self.stats['surface_moyenne_valides']} m²")
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
    """
    Exécution standalone pour tester le tri
    """
    print("=== TEST DU MODULE DE TRI ===")

    try:
        # Créer une instance avec les données par défaut
        sorter = SortScrapSearch()

        # Afficher les statistiques
        sorter.printStats()

        # Proposer d'exporter les résultats
        export_choice = input(
            "\nVoulez-vous exporter les résultats ? (o/N): ").strip().lower()
        if export_choice in ['o', 'oui', 'y', 'yes']:
            filename = input(
                "Nom du fichier (défaut: resultats_tries.json): ").strip()
            if not filename:
                filename = "resultats_tries.json"
            sorter.exportResults(filename)

        print("Test terminé avec succès.")

    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    SortScrapSearch()
