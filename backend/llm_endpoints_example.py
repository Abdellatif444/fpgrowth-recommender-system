# Exemple d'endpoints à ajouter dans backend/app.py
# pour intégrer le service LLM

"""
Ajouter ces imports en haut du fichier app.py :
from llm_service import llm_service
"""

# ============================================================================
# ROUTES LLM - INTELLIGENCE ARTIFICIELLE GÉNÉRATIVE
# ============================================================================

@app.route('/api/llm/explain-recommendation', methods=['POST'])
def explain_recommendation_llm():
    """Générer une explication en langage naturel pour une recommandation"""
    try:
        data = request.get_json()
        basket_items = data.get('basket_items', [])
        recommended_item = data.get('recommended_item', '')
        confidence = data.get('confidence', 0.0)
        lift = data.get('lift', 0.0)
        
        if not basket_items or not recommended_item:
            return jsonify({
                'success': False,
                'error': 'Les items du panier et l\'item recommandé sont requis'
            }), 400
        
        explanation = llm_service.explain_recommendation(
            basket_items=basket_items,
            recommended_item=recommended_item,
            confidence=confidence,
            lift=lift
        )
        
        return jsonify({
            'success': True,
            'explanation': explanation
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/detect-context', methods=['POST'])
def detect_shopping_context():
    """Détecter le contexte d'achat à partir du panier"""
    try:
        data = request.get_json()
        basket_items = data.get('basket_items', [])
        
        if not basket_items:
            return jsonify({
                'success': False,
                'error': 'Le panier ne peut pas être vide'
            }), 400
        
        context = llm_service.detect_shopping_context(basket_items)
        
        return jsonify({
            'success': True,
            'context': context
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/chatbot', methods=['POST'])
def chatbot_interaction():
    """Interface chatbot pour assistance shopping"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Le message ne peut pas être vide'
            }), 400
        
        # Récupérer la liste des produits disponibles si l'analyse a été faite
        available_products = None
        if app_state.get('data_loaded'):
            try:
                top_products = data_loader.get_top_products(50)
                available_products = list(top_products.keys())
            except:
                pass
        
        response = llm_service.chatbot_response(
            user_message=user_message,
            conversation_history=conversation_history,
            available_products=available_products
        )
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/llm/generate-bundle', methods=['POST'])
def generate_product_bundle():
    """Générer une description marketing pour un bundle de produits"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        bundle_name = data.get('bundle_name', None)
        
        if not items or len(items) < 2:
            return jsonify({
                'success': False,
                'error': 'Au moins 2 produits sont requis pour créer un bundle'
            }), 400
        
        description = llm_service.generate_product_bundle_description(
            items=items,
            bundle_name=bundle_name
        )
        
        return jsonify({
            'success': True,
            'bundle_name': bundle_name or f"Pack de {len(items)} produits",
            'description': description,
            'items': items
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
