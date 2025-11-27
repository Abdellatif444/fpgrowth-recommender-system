"""
Module de chargement et préparation des données
"""
import pandas as pd
import os
from datetime import datetime
from database import db

class DataLoader:
    def __init__(self, file_path='data/Online Retail.xlsx'):
        self.file_path = file_path
        self.df = None
    
    def load_data(self):
        """Charger les données (DB ou Excel)"""
        # 1. Essayer de charger depuis la DB
        try:
            print("Vérification des données dans la base de données...")
            df_db = db.get_all_transactions()
            if not df_db.empty:
                print(f"✓ {len(df_db)} transactions chargées depuis la base de données")
                self.df = df_db
                # Convertir les types si nécessaire
                self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
                return self.df
        except Exception as e:
            print(f"Info: Base de données vide ou inaccessible ({e})")

        # 2. Sinon charger depuis Excel
        print(f"Chargement des données depuis {self.file_path}...")
        self.df = pd.read_excel(self.file_path)
        print(f"✓ {len(self.df)} lignes chargées depuis Excel")
        return self.df
    
    def clean_data(self):
        """Nettoyer les données"""
        if self.df is None:
            raise ValueError("Les données doivent être chargées d'abord")
        
        print("Nettoyage des données...")
        initial_count = len(self.df)
        
        # Supprimer les lignes avec des valeurs manquantes critiques
        self.df = self.df.dropna(subset=['InvoiceNo', 'StockCode', 'Description'])
        
        # Supprimer les transactions annulées (InvoiceNo commence par 'C')
        self.df = self.df[~self.df['InvoiceNo'].astype(str).str.startswith('C')]
        
        # Supprimer les quantités négatives ou nulles
        self.df = self.df[self.df['Quantity'] > 0]
        
        # Supprimer les prix négatifs ou nuls
        self.df = self.df[self.df['UnitPrice'] > 0]
        
        # Nettoyer les descriptions
        self.df['Description'] = self.df['Description'].str.strip().str.upper()
        
        # Convertir les types
        self.df['InvoiceNo'] = self.df['InvoiceNo'].astype(str)
        self.df['StockCode'] = self.df['StockCode'].astype(str)
        
        final_count = len(self.df)
        removed = initial_count - final_count
        print(f"✓ {removed} lignes supprimées, {final_count} lignes restantes")
        
        # Sauvegarder dans la base de données si ce n'est pas déjà fait
        try:
            print("Sauvegarde des données nettoyées dans PostgreSQL...")
            # On vérifie d'abord si la table est vide pour éviter les doublons
            existing_count = db.execute_query("SELECT COUNT(*) as count FROM transactions")[0]['count']
            if existing_count == 0:
                db.insert_transactions(self.df)
                print("✓ Données sauvegardées dans la base de données")
            else:
                print("ℹ️ Données déjà présentes dans la base")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde DB: {e}")

        return self.df
    
    def prepare_for_fpgrowth(self):
        """Préparer les données pour l'algorithme FP-Growth"""
        if self.df is None:
            raise ValueError("Les données doivent être chargées et nettoyées d'abord")
        
        print("Préparation des données pour FP-Growth...")
        
        # Grouper par facture et créer des listes de produits
        transactions = self.df.groupby('InvoiceNo')['Description'].apply(list).values.tolist()
        
        print(f"✓ {len(transactions)} transactions préparées")
        
        return transactions
    
    def get_transaction_dataframe(self):
        """Obtenir un DataFrame au format one-hot encoding pour FP-Growth"""
        if self.df is None:
            raise ValueError("Les données doivent être chargées et nettoyées d'abord")
        
        print("Création du DataFrame one-hot encoding...")
        
        # Créer un DataFrame avec InvoiceNo et Description
        basket = self.df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)
        
        # Convertir en booléen (présence/absence)
        # Correction des warnings: utilisation de map() et retour de booléens
        basket_sets = basket.map(lambda x: True if x > 0 else False).astype(bool)
        
        print(f"✓ DataFrame créé: {basket_sets.shape[0]} factures × {basket_sets.shape[1]} produits")
        
        return basket_sets
    
    def get_statistics(self):
        """Obtenir des statistiques sur les données"""
        if self.df is None:
            raise ValueError("Les données doivent être chargées d'abord")
        
        stats = {
            'total_transactions': len(self.df),
            'total_invoices': self.df['InvoiceNo'].nunique(),
            'total_products': self.df['StockCode'].nunique(),
            'total_customers': self.df['CustomerID'].nunique(),
            'total_countries': self.df['Country'].nunique(),
            'date_range': {
                'start': self.df['InvoiceDate'].min().strftime('%Y-%m-%d'),
                'end': self.df['InvoiceDate'].max().strftime('%Y-%m-%d')
            },
            'avg_quantity': float(self.df['Quantity'].mean()),
            'avg_price': float(self.df['UnitPrice'].mean()),
            'total_revenue': float((self.df['Quantity'] * self.df['UnitPrice']).sum())
        }
        
        return stats
    
    def get_top_products(self, n=10):
        """Obtenir les produits les plus vendus"""
        if self.df is None:
            raise ValueError("Les données doivent être chargées d'abord")
        
        top_products = self.df.groupby('Description').agg({
            'Quantity': 'sum',
            'InvoiceNo': 'nunique'
        }).sort_values('Quantity', ascending=False).head(n)
        
        return top_products.to_dict('index')

# Instance globale
data_loader = DataLoader()
