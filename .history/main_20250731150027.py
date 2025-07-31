#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox, ttk
from scrapImmo import ImmoScrap
from SortScrapSearch import SortScrapSearch
from gui import App
from scrapy.crawler import CrawlerProcess
import threading
import time

class MainController:
    def __init__(self):
        self.current_data = {}
        self.sorted_data = {}
        
    def run_scraper(self):
        """Lance le scraper et retourne les données"""
        print("Démarrage du scraping...")
        try:
            # Configuration du processus Scrapy
            process = CrawlerProcess(settings={
                'LOG_LEVEL': 'WARNING',  # Réduit les logs
                'FEEDS': {
                    'res.json': {
                        'format': 'json',
                        'encoding': 'utf8',
                        'overwrite': True,
                    },
                },
            })
            
            process.crawl(ImmoScrap)
            process.start()
            
            # Charger les données scrapées
            if os.path.exists('res.json'):
                with open('res.json', 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                print(f"Scraping terminé. {len(self.current_data)} annonces trouvées.")
                return True
            else:
                print("Erreur: Aucun fichier de résultats généré")
                return False
                
        except Exception as e:
            print(f"Erreur lors du scraping: {e}")
            return False
    
    def sort_data(self):
        """Trie les données en utilisant SortScrapSearch"""
        if not self.current_data:
            print("Aucune donnée à trier")
            return False
            
        try:
            # Créer une instance modifiée de SortScrapSearch
            sorter = SortScrapSearchModified(self.current_data)
            self.sorted_data = {
                'valid': sorter.validSearch,
                'rejected': sorter.rejectedSearch
            }
            
            print(f"Tri terminé:")
            print(f"  - Annonces valides: {len(self.sorted_data['valid'])}")
            print(f"  - Annonces rejetées: {len(self.sorted_data['rejected'])}")
            return True
            
        except Exception as e:
            print(f"Erreur lors du tri: {e}")
            return False
    
    def launch_gui(self):
        """Lance l'interface graphique avec les données"""
        if not self.sorted_data:
            print("Aucune donnée triée disponible")
            return
            
        try:
            app = ImmoApp(self.sorted_data)
            app.mainloop()
        except Exception as e:
            print(f"Erreur lors du lancement de l'interface: {e}")
    
    def run_complete_process(self):
        """Lance le processus complet: scraping -> tri -> interface"""
        print("=== DÉMARRAGE DU PROCESSUS COMPLET ===")
        
        # 1. Scraping
        if not self.run_scraper():
            print("Échec du scraping. Arrêt du processus.")
            return
        
        # 2. Tri des données
        if not self.sort_data():
            print("Échec du tri. Arrêt du processus.")
            return
        
        # 3. Lancement de l'interface
        print("Lancement de l'interface graphique...")
        self.launch_gui()

class SortScrapSearchModified:
    """Version modifiée de SortScrapSearch pour fonctionner avec des données en mémoire"""
    def __init__(self, data):
        self.search = data
        self.rejectedSearch = {}
        self.validSearch = {}
        self.sortSearch()
    
    def sortSearch(self):
        """Trie les données entre valides et rejetées"""
        for key, item in self.search.items():
            if not item.get("colocation", False) and not item.get("studio", False):
                self.validSearch[key] = item
            else:
                self.rejectedSearch[key] = item

class ImmoApp(tk.Tk):
    """Interface graphique améliorée pour afficher les données immobilières"""
    def __init__(self, sorted_data):
        super().__init__()
        
        self.sorted_data = sorted_data
        self.title("Recherche d'Appartements - Dijon")
        self.geometry("1200x800")
        
        self.create_widgets()
        self.populate_data()
    
    def create_widgets(self):
        """Crée les widgets de l'interface"""
        # Notebook pour les onglets
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglet pour les annonces valides
        self.valid_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.valid_frame, text=f"Annonces Valides ({len(self.sorted_data['valid'])})")
        
        # Onglet pour les annonces rejetées
        self.rejected_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rejected_frame, text=f"Annonces Rejetées ({len(self.sorted_data['rejected'])})")
        
        # Création des tableaux
        self.create_treeview(self.valid_frame, "valid_tree")
        self.create_treeview(self.rejected_frame, "rejected_tree")
        
        # Frame pour les boutons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', padx=10, pady=5)
        
        # Boutons d'action
        ttk.Button(button_frame, text="Actualiser les données", 
                  command=self.refresh_data).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Exporter les résultats", 
                  command=self.export_results).pack(side='left', padx=5)
    
    def create_treeview(self, parent, tree_name):
        """Crée un Treeview avec scrollbars"""
        # Frame pour le treeview et scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ("Prix", "Type", "Surface", "Pièces", "Étage", "Équipements", "Description")
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings')
        
        # Configuration des colonnes
        tree.column("#0", width=100, minwidth=100)
        tree.heading("#0", text="ID")
        
        for col in columns:
            tree.column(col, width=150, minwidth=100)
            tree.heading(col, text=col)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Placement
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Binding pour double-clic
        tree.bind("<Double-1>", lambda e: self.open_link(tree))
        
        # Stocker la référence
        setattr(self, tree_name, tree)
    
    def populate_data(self):
        """Remplit les tableaux avec les données"""
        self.populate_tree(self.valid_tree, self.sorted_data['valid'])
        self.populate_tree(self.rejected_tree, self.sorted_data['rejected'])
    
    def populate_tree(self, tree, data):
        """Remplit un arbre avec des données"""
        for key, item in data.items():
            # Extraction des informations
            prix = item.get('prix', 'N/A')
            type_bien = item.get('type', 'N/A')
            
            # Extraction de la surface et pièces depuis specificite
            specificite = item.get('specificite', [])
            surface = next((s for s in specificite if 'm²' in s), 'N/A')
            pieces = next((s for s in specificite if 'pièce' in s), 'N/A')
            etage = next((s for s in specificite if 'Étage' in s), 'N/A')
            
            # Équipements
            equipements = [s for s in specificite if s not in [surface, pieces, etage]]
            equipements_str = ', '.join(equipements[:3])  # Limiter à 3 équipements
            
            # Description tronquée
            description = item.get('description', '')
            description_short = description[:100] + '...' if len(description) > 100 else description
            
            # Insertion dans l'arbre
            tree.insert('', 'end', text=key, values=(
                prix, type_bien, surface, pieces, etage, equipements_str, description_short
            ), tags=(item.get('lien', ''),))
    
    def open_link(self, tree):
        """Ouvre le lien de l'annonce sélectionnée"""
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            if item['tags']:
                link = item['tags'][0]
                import webbrowser
                webbrowser.open(link)
    
    def refresh_data(self):
        """Actualise les données"""
        messagebox.showinfo("Info", "Fonctionnalité d'actualisation à implémenter")
    
    def export_results(self):
        """Exporte les résultats"""
        try:
            with open('resultats_tries.json', 'w', encoding='utf-8') as f:
                json.dump(self.sorted_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Succès", "Résultats exportés dans 'resultats_tries.json'")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")

def main():
    """Fonction principale"""
    print("=== APPLICATION DE RECHERCHE D'APPARTEMENTS ===")
    print("1. Lancement du processus complet (scraping + tri + interface)")
    print("2. Utiliser les données existantes (si disponibles)")
    
    try:
        choice = input("\nVotre choix (1 ou 2): ").strip()
        
        controller = MainController()
        
        if choice == "1":
            controller.run_complete_process()
        elif choice == "2":
            # Essayer de charger les données existantes
            if os.path.exists('res.json'):
                with open('res.json', 'r', encoding='utf-8') as f:
                    controller.current_data = json.load(f)
                if controller.sort_data():
                    controller.launch_gui()
                else:
                    print("Erreur lors du tri des données existantes")
            else:
                print("Aucun fichier de données trouvé. Lancez d'abord le scraping.")
        else:
            print("Choix invalide")
            
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

if __name__ == "__main__":
    main()