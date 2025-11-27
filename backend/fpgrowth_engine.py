"""
Moteur FP-Growth pour l'extraction d'itemsets fréquents et de règles d'association
"""
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
import numpy as np

class FPGrowthEngine:
    def __init__(self, min_support=0.01, min_confidence=0.5):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequent_itemsets = None
        self.rules = None
    
    def find_frequent_itemsets(self, basket_df):
        """
        Trouver les itemsets fréquents avec FP-Growth
        
        Args:
            basket_df: DataFrame one-hot encoding (factures × produits)
        
        Returns:
            DataFrame des itemsets fréquents
        """
        print(f"Recherche des itemsets fréquents (min_support={self.min_support})...")
        
        # Appliquer FP-Growth
        self.frequent_itemsets = fpgrowth(
            basket_df, 
            min_support=self.min_support, 
            use_colnames=True
        )
        
        # Trier par support décroissant
        self.frequent_itemsets = self.frequent_itemsets.sort_values(
            'support', 
            ascending=False
        ).reset_index(drop=True)
        
        print(f"✓ {len(self.frequent_itemsets)} itemsets fréquents trouvés")
        
        return self.frequent_itemsets
    
    def generate_rules(self, metric='confidence', min_threshold=None):
        """
        Générer les règles d'association
        
        Args:
            metric: Métrique à utiliser ('confidence', 'lift', 'leverage', 'conviction')
            min_threshold: Seuil minimum (utilise min_confidence par défaut)
        
        Returns:
            DataFrame des règles d'association
        """
        if self.frequent_itemsets is None:
            raise ValueError("Les itemsets fréquents doivent être calculés d'abord")
        
        if min_threshold is None:
            min_threshold = self.min_confidence
        
        print(f"Génération des règles d'association (min_{metric}={min_threshold})...")
        
        # Générer les règles
        self.rules = association_rules(
            self.frequent_itemsets,
            metric=metric,
            min_threshold=min_threshold
        )
        
        # Trier par confiance et lift
        self.rules = self.rules.sort_values(
            ['confidence', 'lift'], 
            ascending=False
        ).reset_index(drop=True)
        
        print(f"✓ {len(self.rules)} règles générées")
        
        return self.rules
    
    def get_itemsets_by_length(self, length):
        """Obtenir les itemsets d'une longueur spécifique"""
        if self.frequent_itemsets is None:
            return pd.DataFrame()
        
        return self.frequent_itemsets[
            self.frequent_itemsets['itemsets'].apply(lambda x: len(x) == length)
        ]
    
    def get_top_itemsets(self, n=10, min_length=2):
        """Obtenir les top N itemsets par support"""
        if self.frequent_itemsets is None:
            return pd.DataFrame()
        
        filtered = self.frequent_itemsets[
            self.frequent_itemsets['itemsets'].apply(lambda x: len(x) >= min_length)
        ]
        
        return filtered.head(n)
    
    def get_top_rules(self, n=10, min_lift=1.0):
        """Obtenir les top N règles par confiance"""
        if self.rules is None:
            return pd.DataFrame()
        
        filtered = self.rules[self.rules['lift'] >= min_lift]
        
        return filtered.head(n)
    
    def get_rules_for_item(self, item):
        """Obtenir les règles contenant un item spécifique"""
        if self.rules is None:
            return pd.DataFrame()
        
        # Chercher dans les antécédents et conséquents
        mask = self.rules['antecedents'].apply(lambda x: item in x) | \
               self.rules['consequents'].apply(lambda x: item in x)
        
        return self.rules[mask]
    
    def analyze(self, basket_df):
        """
        Effectuer l'analyse complète FP-Growth
        
        Args:
            basket_df: DataFrame one-hot encoding
        
        Returns:
            dict avec itemsets et règles
        """
        # Trouver les itemsets fréquents
        itemsets = self.find_frequent_itemsets(basket_df)
        
        # Générer les règles
        rules = self.generate_rules()
        
        # Statistiques
        stats = {
            'total_itemsets': len(itemsets),
            'itemsets_by_length': {
                i: len(self.get_itemsets_by_length(i))
                for i in range(1, itemsets['itemsets'].apply(len).max() + 1)
            },
            'total_rules': len(rules),
            'avg_confidence': float(rules['confidence'].mean()) if len(rules) > 0 else 0,
            'avg_lift': float(rules['lift'].mean()) if len(rules) > 0 else 0,
            'max_support': float(itemsets['support'].max()),
            'min_support_used': self.min_support,
            'min_confidence_used': self.min_confidence
        }
        
        return {
            'itemsets': itemsets,
            'rules': rules,
            'stats': stats
        }
    
    def format_itemsets_for_json(self, itemsets_df=None):
        """Formater les itemsets pour JSON"""
        if itemsets_df is None:
            itemsets_df = self.frequent_itemsets
        
        if itemsets_df is None or len(itemsets_df) == 0:
            return []
        
        return [
            {
                'items': list(row['itemsets']),
                'support': float(row['support']),
                'length': len(row['itemsets'])
            }
            for _, row in itemsets_df.iterrows()
        ]
    
    def format_rules_for_json(self, rules_df=None):
        """Formater les règles pour JSON"""
        if rules_df is None:
            rules_df = self.rules
        
        if rules_df is None or len(rules_df) == 0:
            return []
        
        return [
            {
                'antecedents': list(row['antecedents']),
                'consequents': list(row['consequents']),
                'support': float(row['support']),
                'confidence': float(row['confidence']),
                'lift': float(row['lift']),
                'leverage': float(row.get('leverage', 0)),
                'conviction': float(row.get('conviction', 0))
            }
            for _, row in rules_df.iterrows()
        ]

# Instance globale
fpgrowth_engine = FPGrowthEngine()
