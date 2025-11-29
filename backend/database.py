"""
Module de connexion à la base de données PostgreSQL
"""
import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

class Database:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'database'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'fpgrowth_db'),
            'user': os.getenv('POSTGRES_USER', 'fpgrowth_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'fpgrowth_pass')
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager pour la connexion à la base de données"""
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query, params=None, fetch=True):
        """Exécuter une requête SQL"""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                return cursor.rowcount
    
    def execute_many(self, query, data):
        """Exécuter une requête avec plusieurs ensembles de paramètres"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, data)
                return cursor.rowcount
    
    def get_stats(self):
        """Obtenir les statistiques de la base de données"""
        query = "SELECT * FROM stats_view"
        result = self.execute_query(query)
        return dict(result[0]) if result else {}
    
    def insert_transactions(self, transactions_df):
        """Insérer les transactions depuis un DataFrame pandas"""
        query = """
            INSERT INTO transactions 
            (invoice_no, stock_code, description, quantity, invoice_date, 
             unit_price, customer_id, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = [
            (
                row['InvoiceNo'],
                row['StockCode'],
                row['Description'],
                row['Quantity'],
                row['InvoiceDate'],
                row['UnitPrice'],
                str(row['CustomerID']) if row['CustomerID'] else None,
                row['Country']
            )
            for _, row in transactions_df.iterrows()
        ]
        return self.execute_many(query, data)
    
    def save_frequent_itemsets(self, itemsets_df):
        """Sauvegarder les itemsets fréquents"""
        # Supprimer les anciens itemsets
        self.execute_query("DELETE FROM frequent_itemsets", fetch=False)
        
        query = """
            INSERT INTO frequent_itemsets (itemset, support, length)
            VALUES (%s, %s, %s)
        """
        data = [
            (
                ','.join(map(str, row['itemsets'])),
                float(row['support']),
                len(row['itemsets'])
            )
            for _, row in itemsets_df.iterrows()
        ]
        return self.execute_many(query, data)
    
    def save_association_rules(self, rules_df):
        """Sauvegarder les règles d'association"""
        # Supprimer les anciennes règles
        self.execute_query("DELETE FROM association_rules", fetch=False)
        
        query = """
            INSERT INTO association_rules 
            (antecedent, consequent, support, confidence, lift, leverage, conviction)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        data = [
            (
                ','.join(map(str, row['antecedents'])),
                ','.join(map(str, row['consequents'])),
                float(row['support']),
                float(row['confidence']),
                float(row['lift']),
                float(row.get('leverage', 0)),
                float(row.get('conviction', 0))
            )
            for _, row in rules_df.iterrows()
        ]
        return self.execute_many(query, data)
    
    def get_association_rules(self, min_confidence=0.5, limit=100):
        """Récupérer les règles d'association"""
        query = """
            SELECT * FROM association_rules 
            WHERE confidence >= %s 
            ORDER BY confidence DESC, lift DESC 
            LIMIT %s
        """
        return self.execute_query(query, (min_confidence, limit))
    
    def save_recommendation(self, input_items, recommended_items, confidence):
        """Sauvegarder une recommandation"""
        query = """
            INSERT INTO recommendations (input_items, recommended_items, confidence)
            VALUES (%s, %s, %s)
        """
        self.execute_query(
            query, 
            (','.join(input_items), ','.join(recommended_items), confidence),
            fetch=False
        )

    def get_all_transactions(self):
        """Récupérer toutes les transactions sous forme de DataFrame"""
        query = """
            SELECT 
                invoice_no as "InvoiceNo",
                stock_code as "StockCode",
                description as "Description",
                quantity as "Quantity",
                invoice_date as "InvoiceDate",
                unit_price as "UnitPrice",
                customer_id as "CustomerID",
                country as "Country"
            FROM transactions
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def clear_all_data(self):
        """Supprimer toutes les données de la base"""
        queries = [
            "TRUNCATE TABLE transactions CASCADE",
            "TRUNCATE TABLE frequent_itemsets CASCADE",
            "TRUNCATE TABLE association_rules CASCADE",
            "TRUNCATE TABLE recommendations CASCADE"
        ]
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                for query in queries:
                    cursor.execute(query)
        return True

# Instance globale
db = Database()