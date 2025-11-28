# 🤖 Guide Rapide - Intégration LLM

## Objectif
Enrichir votre système de recommandation FP-Growth avec l'intelligence artificielle générative via **llmgateway.io**.

---

## 🚀 Démarrage Rapide (15 minutes)

### Étape 1 : Créer un compte LLM Gateway

1. Aller sur **https://llmgateway.io/**
2. Créer un compte gratuit
3. Obtenir votre clé API depuis le dashboard

### Étape 2 : Configuration

1. **Ajouter la clé API dans `.env`** :
   ```bash
   # Ouvrir .env
   nano .env
   
   # Ajouter cette ligne
   LLMGATEWAY_API_KEY=votre_cle_api_ici
   ```

2. **Redémarrer le backend** :
   ```bash
   docker-compose restart backend
   ```

### Étape 3 : Tester l'intégration

1. **Test simple via curl** :
   ```bash
   curl -X POST http://localhost:5000/api/llm/chatbot \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Bonjour, je cherche des décorations pour une fête"
     }'
   ```

2. **Résultat attendu** :
   ```json
   {
     "success": true,
     "response": "Bonjour ! Pour une fête, je vous recommande..."
   }
   ```

---

## 📖 Cas d'Usage Principaux

### 1. Explication de Recommandation

**Endpoint** : `POST /api/llm/explain-recommendation`

**Exemple** :
```bash
curl -X POST http://localhost:5000/api/llm/explain-recommendation \
  -H "Content-Type: application/json" \
  -d '{
    "basket_items": ["WHITE HANGING HEART T-LIGHT HOLDER"],
    "recommended_item": "REGENCY CAKESTAND 3 TIER",
    "confidence": 0.65,
    "lift": 3.2
  }'
```

**Réponse** :
```json
{
  "success": true,
  "explanation": "Les clients qui achètent le photophore cœur blanc recherchent souvent des pièces décoratives élégantes comme ce présentoir à gâteaux 3 étages, parfait pour créer une ambiance raffinée et coordonnée."
}
```

### 2. Détection du Contexte Shopping

**Endpoint** : `POST /api/llm/detect-context`

**Exemple** :
```bash
curl -X POST http://localhost:5000/api/llm/detect-context \
  -H "Content-Type: application/json" \
  -d '{
    "basket_items": [
      "WHITE HANGING HEART T-LIGHT HOLDER",
      "PARTY BUNTING",
      "REGENCY CAKESTAND 3 TIER"
    ]
  }'
```

**Réponse** :
```json
{
  "success": true,
  "context": {
    "context": "Célébration élégante (mariage, anniversaire chic)",
    "style": "Romantique et raffiné",
    "suggestions": [
      "Vaisselle fine assortie",
      "Serviettes en lin blanc",
      "Décorations florales"
    ],
    "reasoning": "Le panier contient des éléments de décoration pour événements festifs..."
  }
}
```

### 3. Chatbot d'Assistance

**Endpoint** : `POST /api/llm/chatbot`

**Exemple** :
```bash
curl -X POST http://localhost:5000/api/llm/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Je veux organiser une fête danniversaire vintage",
    "history": [
      {"role": "user", "content": "Bonjour"},
      {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
    ]
  }'
```

**Réponse** :
```json
{
  "success": true,
  "response": "Super choix pour une fête vintage ! Je vous recommande notre collection rétro : JUMBO BAG RED RETROSPOT, VINTAGE BUNTING, et REGENCY CAKESTAND..."
}
```

### 4. Génération de Bundle

**Endpoint** : `POST /api/llm/generate-bundle`

**Exemple** :
```bash
curl -X POST http://localhost:5000/api/llm/generate-bundle \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      "WHITE HANGING HEART T-LIGHT HOLDER",
      "REGENCY CAKESTAND 3 TIER",
      "PARTY BUNTING"
    ],
    "bundle_name": "Pack Fête Élégante"
  }'
```

**Réponse** :
```json
{
  "success": true,
  "bundle_name": "Pack Fête Élégante",
  "description": "Créez une ambiance festive et raffinée avec ce pack complet ! Le photophore cœur, le présentoir à gâteaux et la guirlande s'harmonisent parfaitement pour une décoration élégante et romantique. Idéal pour mariages, anniversaires ou réceptions chics.",
  "items": [...]
}
```

---

## 🎨 Intégration Frontend

### Bouton "Expliquer" sur les Recommandations

```javascript
// Dans frontend/js/app.js

async function explainRecommendation(basketItems, recommendedItem, confidence, lift) {
    try {
        const response = await apiCall('/llm/explain-recommendation', 'POST', {
            basket_items: basketItems,
            recommended_item: recommendedItem,
            confidence: confidence,
            lift: lift
        });
        
        if (response.success) {
            // Afficher l'explication dans une modal ou tooltip
            showExplanationModal(response.explanation);
        }
    } catch (error) {
        console.error('Erreur LLM:', error);
    }
}

function showExplanationModal(explanation) {
    // Créer une modal avec l'explication
    const modal = document.createElement('div');
    modal.className = 'explanation-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>💡 Pourquoi cette recommandation ?</h3>
            <p>${explanation}</p>
            <button onclick="this.parentElement.parentElement.remove()">Fermer</button>
        </div>
    `;
    document.body.appendChild(modal);
}
```

### Widget Chatbot

```javascript
// Créer un chatbot flottant

class ChatbotWidget {
    constructor() {
        this.history = [];
        this.createWidget();
    }
    
    createWidget() {
        const widget = document.createElement('div');
        widget.id = 'chatbot-widget';
        widget.innerHTML = `
            <div class="chatbot-header" onclick="toggleChatbot()">
                <span>💬 Assistant Shopping</span>
            </div>
            <div class="chatbot-content" id="chatbot-content" style="display:none;">
                <div class="chatbot-messages" id="chatbot-messages"></div>
                <div class="chatbot-input">
                    <input type="text" id="chatbot-input" placeholder="Posez votre question...">
                    <button onclick="sendChatMessage()">Envoyer</button>
                </div>
            </div>
        `;
        document.body.appendChild(widget);
    }
    
    async sendMessage(message) {
        this.addMessage('user', message);
        
        const response = await apiCall('/llm/chatbot', 'POST', {
            message: message,
            history: this.history
        });
        
        if (response.success) {
            this.addMessage('assistant', response.response);
            this.history.push({role: 'user', content: message});
            this.history.push({role: 'assistant', content: response.response});
        }
    }
    
    addMessage(role, content) {
        const messagesDiv = document.getElementById('chatbot-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${role}`;
        messageDiv.textContent = content;
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

// Initialiser au chargement
const chatbot = new ChatbotWidget();
```

---

## 🎯 Prochaines Étapes

### Immédiat (Semaine 1)
1. [ ] Obtenir clé API llmgateway.io
2. [ ] Configurer `.env`
3. [ ] Tester les endpoints LLM
4. [ ] Ajouter le bouton "Expliquer" dans l'interface

### Court terme (Semaine 2-3)
5. [ ] Implémenter le chatbot frontend
6. [ ] Ajouter la détection de contexte sur la page principale
7. [ ] Créer une page "Bundles suggérés"
8. [ ] Optimiser les prompts LLM

### Moyen terme (Mois 1-2)
9. [ ] Ajouter le cache des réponses LLM
10. [ ] Implémenter les bundles automatiques
11. [ ] A/B testing des recommandations LLM vs classiques
12. [ ] Analytics et métriques

---

## 💡 Conseils d'Optimisation

### Réduire les Coûts API
- Cacher les réponses identiques pendant 24h
- Limiter `max_tokens` à 150-200
- Grouper les requêtes si possible

### Améliorer la Qualité
- Tester différents prompts
- Ajouter des exemples dans les prompts (few-shot learning)
- Affiner la température (0.7 = créatif, 0.3 = précis)

### Performance
- Appels LLM asynchrones (ne pas bloquer l'UI)
- Timeout de 10s max
- Fallback si LLM indisponible

---

## 📚 Ressources

- Documentation llmgateway.io : https://llmgateway.io/docs
- Guide des prompts : https://promptingguide.ai/
- Exemples d'intégration : `backend/llm_endpoints_example.py`

---

**Bonne chance avec l'intégration LLM ! 🚀**
