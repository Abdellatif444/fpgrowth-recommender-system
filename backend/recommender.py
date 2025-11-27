"""
Système de recommandation basé sur les règles d'association
"""
import pandas as pd
from typing import List, Dict, Tuple

class Recommender:
    def __init__(self, rules_df=None):
        self.rules = rules_df
    
    def set_rules(self, rules_df):
        """Définir les règles d'association"""
        self.rules = rules_df
    
    def recommend(self, items: List[str], top_n: int = 5, min_confidence: float = 0.5) -> List[Dict]:
        """
        Générer des recommandations basées sur les items fournis
        
        Args:
            items: Liste des items dans le panier
            top_n: Nombre de recommandations à retourner
            min_confidence: Confiance minimum requise
        
        Returns:
            Liste de recommandations avec scores
        """
        if self.rules is None or len(self.rules) == 0:
            return []
        
        items_set = set(items)
        recommendations = {}
        
        # Parcourir les règles
        for _, rule in self.rules.iterrows():
            antecedents = set(rule['antecedents'])
            consequents = set(rule['consequents'])
            
            # Vérifier si les antécédents sont dans les items fournis
            if antecedents.issubset(items_set):
                # Ajouter les conséquents qui ne sont pas déjà dans le panier
                for item in consequents:
                    if item not in items_set:
                        if item not in recommendations:
                            recommendations[item] = {
                                'item': item,
                                'confidence': float(rule['confidence']),
                                'lift': float(rule['lift']),
                                'support': float(rule['support']),
                                'based_on': list(antecedents)
                            }
                        else:
                            # Garder la règle avec la meilleure confiance
                            if rule['confidence'] > recommendations[item]['confidence']:
                                recommendations[item] = {
                                    'item': item,
                                    'confidence': float(rule['confidence']),
                                    'lift': float(rule['lift']),
                                    'support': float(rule['support']),
                                    'based_on': list(antecedents)
                                }
        
        # Filtrer par confiance minimum
        filtered = [
            rec for rec in recommendations.values()
            if rec['confidence'] >= min_confidence
        ]
        
        # Trier par confiance puis lift
        sorted_recs = sorted(
            filtered,
            key=lambda x: (x['confidence'], x['lift']),
            reverse=True
        )
        
        return sorted_recs[:top_n]
    
    def recommend_by_similarity(self, items: List[str], top_n: int = 5) -> List[Dict]:
        """
        Recommander des items similaires basés sur la co-occurrence
        
        Args:
            items: Liste des items
            top_n: Nombre de recommandations
        
        Returns:
            Liste de recommandations
        """
        if self.rules is None or len(self.rules) == 0:
            return []
        
        items_set = set(items)
        similar_items = {}
        
        # Trouver les items qui apparaissent fréquemment avec les items fournis
        for _, rule in self.rules.iterrows():
            all_items = set(rule['antecedents']) | set(rule['consequents'])
            
            # Si au moins un item fourni est dans la règle
            if items_set & all_items:
                # Ajouter les autres items
                for item in all_items:
                    if item not in items_set:
                        if item not in similar_items:
                            similar_items[item] = {
                                'item': item,
                                'score': float(rule['lift']),
                                'support': float(rule['support'])
                            }
                        else:
                            # Accumuler le score
                            similar_items[item]['score'] += float(rule['lift'])
        
        # Trier par score
        sorted_items = sorted(
            similar_items.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_items[:top_n]
    
    def get_frequently_bought_together(self, item: str, top_n: int = 5) -> List[Dict]:
        """
        Trouver les items fréquemment achetés avec un item donné
        
        Args:
            item: Item de référence
            top_n: Nombre de résultats
        
        Returns:
            Liste d'items fréquemment achetés ensemble
        """
        if self.rules is None or len(self.rules) == 0:
            return []
        
        together = {}
        
        for _, rule in self.rules.iterrows():
            antecedents = set(rule['antecedents'])
            consequents = set(rule['consequents'])
            
            # Si l'item est dans les antécédents
            if item in antecedents:
                for cons_item in consequents:
                    if cons_item not in together:
                        together[cons_item] = {
                            'item': cons_item,
                            'confidence': float(rule['confidence']),
                            'lift': float(rule['lift']),
                            'support': float(rule['support'])
                        }
                    else:
                        # Garder la meilleure confiance
                        if rule['confidence'] > together[cons_item]['confidence']:
                            together[cons_item]['confidence'] = float(rule['confidence'])
                            together[cons_item]['lift'] = float(rule['lift'])
            
            # Si l'item est dans les conséquents
            if item in consequents:
                for ant_item in antecedents:
                    if ant_item not in together:
                        together[ant_item] = {
                            'item': ant_item,
                            'confidence': float(rule['confidence']),
                            'lift': float(rule['lift']),
                            'support': float(rule['support'])
                        }
        
        # Trier par confiance
        sorted_together = sorted(
            together.values(),
            key=lambda x: x['confidence'],
            reverse=True
        )
        
        return sorted_together[:top_n]
    
    def explain_recommendation(self, item: str, based_on: List[str]) -> Dict:
        """
        Expliquer pourquoi un item est recommandé
        
        Args:
            item: Item recommandé
            based_on: Items sur lesquels la recommandation est basée
        
        Returns:
            Explication détaillée
        """
        if self.rules is None:
            return {}
        
        based_on_set = set(based_on)
        
        # Trouver la règle correspondante
        for _, rule in self.rules.iterrows():
            if set(rule['antecedents']) == based_on_set and item in rule['consequents']:
                return {
                    'item': item,
                    'based_on': based_on,
                    'confidence': float(rule['confidence']),
                    'lift': float(rule['lift']),
                    'support': float(rule['support']),
                    'explanation': f"Les clients qui ont acheté {', '.join(based_on)} "
                                 f"ont également acheté {item} dans {rule['confidence']*100:.1f}% des cas. "
                                 f"Cette association est {rule['lift']:.2f}x plus forte que le hasard."
                }
        
        return {}

# Instance globale
recommender = Recommender()
