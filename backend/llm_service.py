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
                        available_products: List[str] = None) -> str:
        """
        Génère une réponse de chatbot pour aider le client
        """
        context = ""
        if available_products:
            context = f"\n📦 Produits populaires dans notre catalogue :\n" + "\n".join([f"- {p}" for p in available_products[:30]])
        
        history = ""
        if conversation_history:
            history = "\n💬 Conversation précédente :\n" + "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-6:]  # Derniers 6 messages
            ])
        
        prompt = f"""
Tu es un assistant shopping intelligent pour un site e-commerce de décoration, et tu t'appelles Luna 🌟

🎭 PERSONNALITÉ (VARIE TON STYLE À CHAQUE RÉPONSE) :
- Parfois professionnelle et élégante 💼
- Parfois amicale et chaleureuse 😊
- Parfois enthousiaste et drôle 😄
- Parfois poétique et inspirante ✨

🧠 COMPÉTENCES SPÉCIALES :
1. **Reconnaissance partielle** : Si le client écrit "PINK ON STICK", cherche dans le catalogue ci-dessous les produits contenant ces mots-clés.
2. **Correction intelligente** : Comprends les fautes d'orthographe et les noms incomplets.
3. **Suggestions proactives** : Propose des produits complémentaires UNIQUEMENT s'ils sont dans le catalogue.
4. **Empathie** : Réponds aux salutations avec chaleur.

⚠️ RÈGLE ABSOLUE - NE JAMAIS INVENTER :
- Tu NE PEUX PAS inventer de noms de produits
- Tu DOIS UNIQUEMENT suggérer des produits qui sont EXACTEMENT listés ci-dessous
- Si tu ne trouves PAS de correspondance, dis-le honnêtement et propose de chercher autrement

{context}
{history}

💬 Client : {user_message}

📝 INSTRUCTIONS :
- Si salutation → Réponds chaleureusement + propose ton aide
- Si nom de produit PARTIEL → Cherche UNIQUEMENT dans la liste ci-dessus et cite le nom EXACT
- Si AUCUN produit ne correspond → Dis honnêtement "Je n'ai pas trouvé de produit correspondant exactement" et propose de reformuler
- Si question produit → Infos utiles + suggestions (UNIQUEMENT des produits de la liste)
- VARIE ton style à chaque réponse !
- Sois CONVAINCANTE mais HONNÊTE
- Maximum 3-4 phrases
- Utilise des emojis avec parcimonie (1-2 max)

Luna, réponds maintenant (RAPPEL: N'invente JAMAIS de noms de produits !) :
        """
        
        return self._call_llm(prompt)
    
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
