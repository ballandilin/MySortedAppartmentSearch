#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application de démarrage rapide pour tester avec les données existantes
Ce fichier permet de tester l'application sans avoir besoin d'installer Scrapy
"""

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox, ttk
import webbrowser
from datetime import datetime

# Ajouter le répertoire courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from SortScrapSearch import SortScrapSearch
except ImportError as e:
    print(f"Erreur d'import: {e}")
    sys.exit(1)


class QuickStartApp:
    """Application de démarrage rapide utilisant les données existantes"""

    def __init__(self):
        self.data_files = self.find_data_files()
        self.sorted_data = None

    def find_data_files(self):
        """Trouve les fichiers de données disponibles"""
        possible_files = [
            "res.json",
            "res_detailed.json",
            "files/seLoger1.json",
            "resultats_tries.json"
        ]

        found_files = []
        for file_path in possible_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        file_size = len(data) if isinstance(data, dict) else 0
                        found_files.append({
                            'path': file_path,
                            'size': file_size,
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path))
                        })
                except Exception as e:
                    print(f"Erreur lors de la lecture de {file_path}: {e}")

        return found_files

    def display_available_files(self):
        """Affiche les fichiers de données disponibles"""
        if not self.data_files:
            print("Aucun fichier de données trouvé.")
            print(
                "Veuillez d'abord lancer le scraping ou placer des fichiers de données dans le répertoire.")
            return False

        print("\nFichiers de données disponibles:")
        print("-" * 60)
        for i, file_info in enumerate(self.data_files, 1):
            print(f"{i}. {file_info['path']}")
            print(f"   Nombre d'entrées: {file_info['size']}")
            print(
                f"   Modifié le: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
            print()

        return True

    def select_data_file(self):
        """Permet à l'utilisateur de sélectionner un fichier de données"""
        if not self.display_available_files():
            return None

        try:
            choice = input(
                f"Choisissez un fichier (1-{len(self.data_files)}): ").strip()
            choice_num = int(choice)

            if 1 <= choice_num <= len(self.data_files):
                selected_file = self.data_files[choice_num - 1]
                print(f"\nFichier sélectionné: {selected_file['path']}")
                return selected_file['path']
            else:
                print("Choix invalide.")
                return None

        except ValueError:
            print("Veuillez entrer un nombre valide.")
            return None

    def load_and_sort_data(self, file_path):
        """Charge et trie les données"""
        try:
            print(f"\nChargement des données depuis {file_path}...")

            # Créer une instance de SortScrapSearch
            sorter = SortScrapSearch(file_path)

            # Afficher les statistiques
            sorter.printStats()

            # Préparer les données pour l'interface
            self.sorted_data = {
                'valid': sorter.getValidAnnouncements(),
                'rejected': sorter.getRejectedAnnouncements(),
                'stats': sorter.stats
            }

            return True

        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            return False

    def launch_gui(self):
        """Lance l'interface graphique"""
        if not self.sorted_data:
            print("Aucune donnée disponible pour l'interface.")
            return

        try:
            print("Lancement de l'interface graphique...")
            app = QuickImmoApp(self.sorted_data)
            app.mainloop()
        except Exception as e:
            print(f"Erreur lors du lancement de l'interface: {e}")

    def run(self):
        """Lance l'application complète"""
        print("=== APPLICATION RECHERCHE APPARTEMENTS - DÉMARRAGE RAPIDE ===")
        print("Cette version utilise les données existantes sans scraping.")
        print()

        # Sélection du fichier
        file_path = self.select_data_file()
        if not file_path:
            return

        # Chargement et tri
        if not self.load_and_sort_data(file_path):
            return

        # Lancement de l'interface
        self.launch_gui()


class QuickImmoApp(tk.Tk):
    """Interface graphique simplifiée pour l'affichage des données"""

    def __init__(self, sorted_data):
        super().__init__()

        self.sorted_data = sorted_data
        self.title("Recherche d'Appartements - Dijon (Données existantes)")
        self.geometry("1400x900")
        self.configure(bg='#f0f0f0')

        self.create_widgets()
        self.populate_data()

    def create_widgets(self):
        """Crée l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Frame pour les statistiques
        stats_frame = ttk.LabelFrame(
            main_frame, text="Statistiques", padding="10")
        stats_frame.pack(fill='x', pady=(0, 10))

        self.create_stats_display(stats_frame)

        # Notebook pour les onglets
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)

        # Onglets
        self.create_tab("valid", "Annonces Valides", "green")
        self.create_tab("rejected", "Annonces Rejetées", "red")

        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))

        self.create_buttons(button_frame)

    def create_stats_display(self, parent):
        """Crée l'affichage des statistiques"""
        stats = self.sorted_data.get('stats', {})

        stats_text = f"""Total: {stats.get('total_annonces', 0)} | """
        stats_text += f"Valides: {stats.get('annonces_valides', 0)} | """
        stats_text += f"Rejetées: {stats.get('annonces_rejetees', 0)} | """
        stats_text += f"Taux validation: {stats.get('taux_validation', 0)}% | """
        stats_text += f"Prix moyen: {stats.get('prix_moyen_valides', 0)} € | """
        stats_text += f"Surface moyenne: {stats.get('surface_moyenne_valides', 0)} m²"""

        ttk.Label(parent, text=stats_text, font=('Arial', 10, 'bold')).pack()

    def create_tab(self, data_key, title, color):
        """Crée un onglet avec son tableau"""
        frame = ttk.Frame(self.notebook)
        data = self.sorted_data.get(data_key, {})
        tab_title = f"{title} ({len(data)})"
        self.notebook.add(frame, text=tab_title)

        # Créer le treeview
        tree = self.create_treeview(frame)
        setattr(self, f"{data_key}_tree", tree)

        return frame

    def create_treeview(self, parent):
        """Crée un Treeview avec colonnes et scrollbars"""
        # Frame conteneur
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Colonnes
        columns = ("Prix", "Type", "Localisation", "Surface",
                   "Pièces", "Équipements", "Colocation", "Studio")

        # Treeview
        tree = ttk.Treeview(tree_frame, columns=columns,
                            show='tree headings', height=20)

        # Configuration des colonnes
        tree.column("#0", width=80, minwidth=80)
        tree.heading("#0", text="ID")

        column_widths = [100, 150, 200, 80, 80, 200, 80, 80]
        for i, (col, width) in enumerate(zip(columns, column_widths)):
            tree.column(col, width=width, minwidth=width)
            tree.heading(col, text=col, anchor='w')

        # Scrollbars
        v_scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=tree.yview)
        h_scrollbar = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set,
                       xscrollcommand=h_scrollbar.set)

        # Placement avec grid
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Événements
        tree.bind("<Double-1>", lambda e: self.on_double_click(tree))
        tree.bind("<Button-3>", lambda e: self.show_context_menu(e, tree))

        return tree

    def create_buttons(self, parent):
        """Crée les boutons d'action"""
        ttk.Button(parent, text="Exporter les résultats",
                   command=self.export_results).pack(side='left', padx=5)

        ttk.Button(parent, text="Rafraîchir",
                   command=self.refresh_display).pack(side='left', padx=5)

        ttk.Button(parent, text="Statistiques détaillées",
                   command=self.show_detailed_stats).pack(side='left', padx=5)

    def populate_data(self):
        """Remplit les tableaux avec les données"""
        self.populate_tree(self.valid_tree, self.sorted_data.get('valid', {}))
        self.populate_tree(self.rejected_tree,
                           self.sorted_data.get('rejected', {}))

    def populate_tree(self, tree, data):
        """Remplit un tableau avec des données"""
        # Vider le tableau
        for item in tree.get_children():
            tree.delete(item)

        # Remplir avec les nouvelles données
        for key, item in data.items():
            # Extraction des informations
            prix = item.get('prix', 'N/A')
            type_bien = item.get('type', 'N/A')
            localisation = item.get('localisation', 'N/A')

            # Surface et pièces
            surface = f"{item.get('surface_m2', 'N/A')} m²" if item.get(
                'surface_m2') else 'N/A'
            pieces = f"{item.get('nombre_pieces', 'N/A')}" if item.get(
                'nombre_pieces') else 'N/A'

            # Équipements depuis spécificités
            specificites = item.get('specificite', [])
            equipements = ', '.join(
                [s for s in specificites if 'Étage' not in s and 'm²' not in s and 'pièce' not in s][:3])

            # Indicateurs
            colocation = "Oui" if item.get('colocation', False) else "Non"
            studio = "Oui" if item.get('studio', False) else "Non"

            # Insertion
            tree.insert('', 'end', text=key, values=(
                prix, type_bien, localisation, surface, pieces, equipements, colocation, studio
            ), tags=(item.get('lien', ''),))

    def on_double_click(self, tree):
        """Gère le double-clic sur une ligne"""
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            if item['tags'] and item['tags'][0]:
                link = item['tags'][0]
                try:
                    webbrowser.open(link)
                except Exception as e:
                    messagebox.showerror(
                        "Erreur", f"Impossible d'ouvrir le lien: {e}")

    def show_context_menu(self, event, tree):
        """Affiche un menu contextuel"""
        # À implémenter si nécessaire
        pass

    def export_results(self):
        """Exporte les résultats"""
        try:
            filename = f"export_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.sorted_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Succès", f"Données exportées dans {filename}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")

    def refresh_display(self):
        """Rafraîchit l'affichage"""
        self.populate_data()
        messagebox.showinfo("Info", "Affichage rafraîchi")

    def show_detailed_stats(self):
        """Affiche des statistiques détaillées"""
        stats = self.sorted_data.get('stats', {})

        stats_window = tk.Toplevel(self)
        stats_window.title("Statistiques détaillées")
        stats_window.geometry("400x300")

        text_widget = tk.Text(stats_window, wrap='word', padx=10, pady=10)
        text_widget.pack(fill='both', expand=True)

        stats_text = "STATISTIQUES DÉTAILLÉES\n"
        stats_text += "=" * 30 + "\n\n"

        for key, value in stats.items():
            key_formatted = key.replace('_', ' ').title()
            stats_text += f"{key_formatted}: {value}\n"

        text_widget.insert('1.0', stats_text)
        text_widget.config(state='disabled')


def main():
    """Fonction principale du démarrage rapide"""
    try:
        app = QuickStartApp()
        app.run()
    except KeyboardInterrupt:
        print("\nArrêt demandé par l'utilisateur")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
