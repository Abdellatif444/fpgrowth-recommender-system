"""
Service d'intégration LLM via Groq API
"""
import os
import requests
from typing import List, Dict, Optional

class LLMService:
    def __init__(self):
        self.api_key = os.getenv('LLMGATEWAY_API_KEY', '')
        self.base_url = "https://api.groq.com/openai/v1"
        self.model = "llama-3.3-70b-versatile"  # Dernier modèle Llama 3.3
    
    def explain_recommendation(self, 
                              basket_items: List[str], 
                              recommended_item: str,
                              confidence: float,
                              lift: float) -> str:
        """
        Génère une explication en langage naturel pour une recommandation
        """
        prompt = f"""
        En tant qu'expert en e-commerce, explique pourquoi ce produit est recommandé :
        
        Panier actuel : {', '.join(basket_items)}
        Produit recommandé : {recommended_item}
        Confiance : {confidence:.1%}
        Force d'association (lift) : {lift:.2f}
        
        Fournis une explication courte (max 2 phrases) et engageante pour le client.
        Mets en avant la synergie entre les produits.
        """
        
        return self._call_llm(prompt)
    
    def detect_shopping_context(self, basket_items: List[str]) -> Dict:
        """
        Détecte le contexte d'achat (événement, thème, besoin)
        """
        prompt = f"""
        Analyse ce panier d'achat et détermine :
        1. Le contexte probable (mariage, anniversaire, décoration maison, etc.)
        2. Le style détecté (moderne, vintage, élégant, etc.)
        3. 3 suggestions de produits complémentaires
        
        Panier : {', '.join(basket_items)}
        
        Réponds au format JSON :
        {{
            "context": "...",
            "style": "...",
            "suggestions": ["...", "...", "..."],
            "reasoning": "..."
        }}
        """
        
        response = self._call_llm(prompt)
        try:
            import json
            return json.loads(response)
        except:
            return {
                "context": "Non détecté",
                "style": "Mixte",
                "suggestions": [],
                "reasoning": response
            }
    
    def generate_product_bundle_description(self, 
                                           items: List[str],
                                           bundle_name: str = None) -> str:
        """
        Génère une description marketing pour un bundle de produits
        """
        prompt = f"""
        Crée une description marketing attractive pour ce bundle de produits :
        
        Produits : {', '.join(items)}
        Nom du bundle : {bundle_name or 'Pack Spécial'}
        
        La description doit :
        - Être courte (max 3 phrases)
        - Mettre en avant la complémentarité des produits
        - Donner envie d'acheter
        - Être en français
        """
        
        return self._call_llm(prompt)
    
    def chatbot_response(self, 
                        user_message: str,
                        conversation_history: List[Dict] = None,
                        available_products: List[str] = None,
                        user_cart: List = None,
                        fp_recommendations: List[str] = None) -> str:
        """
        Génère une réponse de chatbot pour aider le client
        """
        # Vérifier si c'est la première interaction
        is_first_message = not conversation_history or len(conversation_history) <= 1
        
        context = ""
        if available_products:
            context = f"\n📦 CATALOGUE COMPLET (noms EXACTS avec prix) :\n" + "\n".join([f"- {p}" for p in available_products[:100]])
        
        cart_context = ""
        if user_cart and len(user_cart) > 0:
            cart_items = [item['name'] if isinstance(item, dict) else item for item in user_cart]
            cart_context = f"\n🛒 PANIER ACTUEL DU CLIENT :\n" + "\n".join([f"- {item}" for item in cart_items])
        
        recommendations_context = ""
        if fp_recommendations and len(fp_recommendations) > 0:
            recommendations_context = f"\n✨ RECOMMANDATIONS PRIORITAIRES (basées sur 19,000+ transactions réelles - FP-Growth) :\n" + "\n".join([f"- {rec}" for rec in fp_recommendations])
            recommendations_context += "\n⚠️ IMPORTANT : Ces produits sont PROUVÉS comme étant souvent achetés ensemble. Propose-les en PRIORITÉ avec des arguments convaincants !"
        
        history = ""
        if conversation_history and len(conversation_history) > 1:
            history = "\n💬 HISTORIQUE DE CONVERSATION :\n" + "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-8:]  # Derniers 8 messages
            ])
        
        greeting_instruction = "- NE TE PRÉSENTE PAS (tu l'as déjà fait)" if not is_first_message else "- Présente-toi comme Luna 🌟, assistante shopping"
        
        prompt = f"""
Tu es Luna, une assistante shopping EXPERTE et PERSUASIVE pour un site e-commerce de décoration.

🎯 MISSION : Être LA MEILLEURE conseillère shopping - convaincante, précise, et intelligente.

🧠 RÈGLES ABSOLUES :
1. **HISTORIQUE** : {greeting_instruction}
2. **NE JAMAIS INVENTER** : Utilise UNIQUEMENT les noms EXACTS du catalogue ci-dessous
3. **PRIORITÉ FP-GROWTH** : Si des recommandations FP-Growth sont données, PROPOSE-LES EN PREMIER avec des arguments comme :
   - "D'après l'analyse de milliers d'achats clients..."
   - "Les clients qui ont acheté X adorent également Y parce que..."
   - "Ces produits forment un ensemble parfait car..."
4. **PRÉCISION** : Cite les noms de produits EXACTEMENT comme dans le catalogue (ex: "PAPER CRAFT , LITTLE BIRDIE" pas "LITTLE BIRDIE")
5. **PRIX** : Mentionne les prix pour créer de la valeur
6. **CONVICTION** : Sois PERSUASIVE, pas seulement informative

{context}
{cart_context}
{recommendations_context}
{history}

💬 CLIENT : {user_message}

📝 INSTRUCTIONS DÉTAILLÉES :
- Si le message est incompréhensible ou très court (ex: "j", "jjj") → Dis simplement : "Je ne comprends pas, pouvez-vous m'expliquer ?"
- Si PREMIÈRE interaction → Présente-toi chaleureusement comme Luna
- Si interaction SUIVANTE → VA DROIT AU BUT, pas de répétition de présentation
- Si le client demande des suggestions ET qu'il a un panier :
  1. Utilise les RECOMMANDATIONS FP-GROWTH en priorité
  2. Explique POURQUOI ces produits vont ensemble (synergie, style, usage)
  3. Mentionne le prix pour justifier la valeur
  4. Sois CONVAINCANTE : "Vous allez adorer..." / "Parfait pour compléter..." / "Un choix populaire..."
- Si recherche de produit → Trouve la correspondance EXACTE dans le catalogue
- Si produit non trouvé → Propose de reformuler ou suggère des alternatives similaires
- VARIE ton style à chaque réponse (professionnelle, amicale, enthousiaste, etc.)
- Maximum 5 phrases, concises et percutantes
- 1-2 emojis max

Luna, réponds maintenant (RAPPEL: Priorise FP-Growth et sois PERSUASIVE !) :
        """
        
        return self._call_llm(prompt, max_tokens=350)
    
    def _call_llm(self, prompt: str, max_tokens: int = 250) -> str:
        """
        Appelle l'API Groq
        """
        if not self.api_key:
            return "LLM non configuré (API key manquante)"
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.8  # Plus de créativité pour Luna
                },
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                return f"Erreur LLM : {response.status_code}"
                
        except Exception as e:
            return f"Erreur lors de l'appel au LLM : {str(e)}"

# Instance globale
llm_service = LLMService()
