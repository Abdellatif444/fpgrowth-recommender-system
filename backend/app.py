"""
API Flask pour le système de recommandation FP-Growth
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import time
from datetime import datetime

# Imports des modules locaux
from database import db
from data_loader import data_loader
from fpgrowth_engine import fpgrowth_engine
from recommender import recommender
from llm_service import llm_service
from products_manager import products_manager
import pandas as pd
import uuid

# Initialisation de l'application Flask
# On configure le dossier static pour pointer vers le dossier frontend
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JSON_SORT_KEYS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join('..', 'frontend', 'images', 'products')
# Debug: Afficher le chemin absolu
print(f"DEBUG: UPLOAD_FOLDER (relative): {app.config['UPLOAD_FOLDER']}")
print(f"DEBUG: UPLOAD_FOLDER (absolute): {os.path.abspath(app.config['UPLOAD_FOLDER'])}")

# ============================================================================
# ROUTES FICHIERS STATIQUES
# ============================================================================

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve_static(path):
    return app.send_static_file(path)

# @app.route('/images/products/<filename>')
# def serve_product_image(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# État de l'application
app_state = {
    'data_loaded': False,
    'analysis_done': False,
    'last_analysis': None
}

# ============================================================================
# ROUTES DE SANTÉ ET INFORMATION
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Vérifier l'état de l'API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'data_loaded': app_state['data_loaded'],
        'analysis_done': app_state['analysis_done']
    })

@app.route('/api/info', methods=['GET'])
def get_info():
    """Obtenir les informations sur l'application"""
    return jsonify({
        'name': 'FP-Growth Recommender System',
        'version': '1.0.0',
        'authors': ['Student A', 'Student Y'],
        'institution': 'EHTP - École Hassania des Travaux Publics',
        'algorithm': 'FP-Growth (Frequent Pattern Growth)',
        'state': app_state
    })

# ============================================================================
# ROUTES D'AUTHENTIFICATION
# ============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Authentification simple"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Admin credentials (hardcoded for demo)
    if username == 'admin' and password == 'admin123':
        return jsonify({
            'success': True,
            'role': 'admin',
            'token': str(uuid.uuid4())
        })
    
    # User credentials (hardcoded for demo)
    if username == 'client' and password == 'client123':
        return jsonify({
            'success': True,
            'role': 'client',
            'token': str(uuid.uuid4())
        })
        
    return jsonify({
        'success': False,
        'error': 'Identifiants invalides'
    }), 401

# ============================================================================
# ROUTES DE GESTION DES PRODUITS (ADMIN)
# ============================================================================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Obtenir la liste des produits avec métadonnées"""
    # Récupérer les métadonnées existantes
    metadata = products_manager.get_all_products()
    
    # Récupérer les produits depuis les transactions (si chargées)
    products_list = []
    if app_state.get('data_loaded'):
        try:
            # On récupère un grand nombre de produits pour avoir une liste complète
            top_products = data_loader.get_top_products(1000)
            
            for name, stats in top_products.items():
                product_data = metadata.get(name, {})
                products_list.append({
                    'name': name,
                    'sales_count': stats['Quantity'],
                    'price': product_data.get('price', 0),
                    'description': product_data.get('description', ''),
                    'image': product_data.get('image', '')
                })
        except Exception as e:
            print(f"Erreur lors de la récupération des produits: {e}")
            
    # Si pas de données chargées, on retourne juste les métadonnées
    if not products_list:
        for name, data in metadata.items():
            products_list.append({
                'name': name,
                'sales_count': 0,
                'price': data.get('price', 0),
                'description': data.get('description', ''),
                'image': data.get('image', '')
            })
            
    return jsonify({
        'success': True,
        'products': products_list
    })

@app.route('/api/products', methods=['POST'])
def update_product():
    """Mettre à jour ou ajouter un produit"""
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    description = data.get('description')
    image_url = data.get('image')
    
    if not name:
        return jsonify({'success': False, 'error': 'Nom du produit requis'}), 400
        
    updated_product = products_manager.update_product(name, price, description, image_url)
    return jsonify({
        'success': True,
        'product': updated_product
    })

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    """Uploader une image de produit"""
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier image'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nom de fichier vide'}), 400
        
    image_path = products_manager.save_image(file)
    if image_path:
        return jsonify({
            'success': True,
            'image_path': image_path
        })
    
    return jsonify({'success': False, 'error': 'Erreur lors de l\'upload'}), 500

# ============================================================================
# ROUTES D'ACHAT (CLIENT)
# ============================================================================

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Traiter une commande et l'ajouter aux données"""
    try:
        data = request.get_json()
        cart_items = data.get('items', [])
        
        if not cart_items:
            return jsonify({'success': False, 'error': 'Panier vide'}), 400
            
        # Créer une nouvelle facture (InvoiceNo)
        # On utilise un timestamp ou un ID unique
        invoice_no = f"NEW-{int(time.time())}"
        invoice_date = datetime.now()
        
        # Préparer les données pour le DataFrame
        rows = []
        for item in cart_items:
            rows.append({
                'InvoiceNo': invoice_no,
                'StockCode': 'MANUAL', # Code générique
                'Description': item['name'],
                'Quantity': int(item.get('quantity', 1)),
                'InvoiceDate': invoice_date,
                'UnitPrice': float(item.get('price', 0)),
                'CustomerID': 99999, # ID générique pour les nouveaux clients
                'Country': 'France'
            })
            
        df_new = pd.DataFrame(rows)
        
        # Insérer dans la base de données
        db.insert_transactions(df_new)
        
        # Mettre à jour le DataLoader en mémoire si nécessaire
        # (Optionnel : on pourrait recharger tout, mais c'est lourd. 
        # Pour l'instant, on suppose que le prochain rechargement prendra les nouvelles données)
        
        return jsonify({
            'success': True,
            'message': 'Commande enregistrée avec succès',
            'invoice_no': invoice_no
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ROUTES DE GESTION DES DONNÉES
# ============================================================================

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Charger et nettoyer les données"""
    try:
        start_time = time.time()
        
        # Vérifier si les données sont déjà en mémoire
        if data_loader.df is not None and not data_loader.df.empty:
            print("✓ Données déjà présentes en mémoire, rechargement évité")
            stats = data_loader.get_statistics()
            app_state['data_loaded'] = True
            
            return jsonify({
                'success': True,
                'message': 'Données déjà chargées (depuis la mémoire)',
                'stats': stats,
                'elapsed_time': '0.00s',
                'from_cache': True
            })
        
        # Sinon, charger les données
        data_loader.load_data()
        
        # Nettoyer les données
        df = data_loader.clean_data()
        
        # Insérer dans la base de données
        db.insert_transactions(df)
        
        # Obtenir les statistiques
        stats = data_loader.get_statistics()
        
        app_state['data_loaded'] = True
        
        elapsed_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'message': 'Données chargées et nettoyées avec succès',
            'stats': stats,
            'elapsed_time': f'{elapsed_time:.2f}s',
            'from_cache': False
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear-data', methods=['POST'])
def clear_data():
    """Supprimer toutes les données de la base et de la mémoire"""
    try:
        # Supprimer de la base de données
        db.clear_all_data()
        
        # Réinitialiser la mémoire
        data_loader.df = None
        
        # Mettre à jour l'état
        app_state['data_loaded'] = False
        app_state['analysis_done'] = False
        app_state['last_analysis'] = None
        
        return jsonify({
            'success': True,
            'message': 'Toutes les données ont été supprimées avec succès'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtenir les statistiques des données"""
    try:
        if not app_state['data_loaded']:
            return jsonify({
                'success': False,
                'error': 'Les données doivent être chargées d\'abord'
            }), 400
        
        stats = data_loader.get_statistics()
        db_stats = db.get_stats()
        
        return jsonify({
            'success': True,
            'data_stats': stats,
            'database_stats': db_stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/top-products', methods=['GET'])
def get_top_products():
    """Obtenir les produits les plus vendus"""
    try:
        n = request.args.get('n', default=10, type=int)
        
        if not app_state['data_loaded']:
            return jsonify({
                'success': False,
                'error': 'Les données doivent être chargées d\'abord'
            }), 400
        
        top_products = data_loader.get_top_products(n)
        
        return jsonify({
            'success': True,
            'top_products': top_products
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ROUTES D'ANALYSE FP-GROWTH
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_fpgrowth():
    """Effectuer l'analyse FP-Growth"""
    try:
        if not app_state['data_loaded']:
            return jsonify({
                'success': False,
                'error': 'Les données doivent être chargées d\'abord'
            }), 400
        
        start_time = time.time()
        
        # Récupérer les paramètres
        data = request.get_json() or {}
        min_support = data.get('min_support', 0.01)
        min_confidence = data.get('min_confidence', 0.5)
        
        # Configurer le moteur
        fpgrowth_engine.min_support = min_support
        fpgrowth_engine.min_confidence = min_confidence
        
        # Préparer les données
        basket_df = data_loader.get_transaction_dataframe()
        
        # Effectuer l'analyse
        results = fpgrowth_engine.analyze(basket_df)
        
        # Sauvegarder dans la base de données
        db.save_frequent_itemsets(results['itemsets'])
        db.save_association_rules(results['rules'])
        
        # Configurer le recommender
        recommender.set_rules(results['rules'])
        
        app_state['analysis_done'] = True
        app_state['last_analysis'] = datetime.now().isoformat()
        
        elapsed_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'message': 'Analyse FP-Growth terminée avec succès',
            'stats': results['stats'],
            'elapsed_time': f'{elapsed_time:.2f}s'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/itemsets', methods=['GET'])
def get_itemsets():
    """Obtenir les itemsets fréquents"""
    try:
        if not app_state['analysis_done']:
            return jsonify({
                'success': False,
                'error': 'L\'analyse doit être effectuée d\'abord'
            }), 400
        
        # Paramètres
        top_n = request.args.get('top_n', default=20, type=int)
        min_length = request.args.get('min_length', default=2, type=int)
        
        # Obtenir les itemsets
        top_itemsets = fpgrowth_engine.get_top_itemsets(top_n, min_length)
        
        return jsonify({
            'success': True,
            'itemsets': fpgrowth_engine.format_itemsets_for_json(top_itemsets),
            'total': len(fpgrowth_engine.frequent_itemsets)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Obtenir les règles d'association"""
    try:
        if not app_state['analysis_done']:
            return jsonify({
                'success': False,
                'error': 'L\'analyse doit être effectuée d\'abord'
            }), 400
        
        # Paramètres
        top_n = request.args.get('top_n', default=20, type=int)
        min_lift = request.args.get('min_lift', default=1.0, type=float)
        
        # Obtenir les règles
        top_rules = fpgrowth_engine.get_top_rules(top_n, min_lift)
        
        return jsonify({
            'success': True,
            'rules': fpgrowth_engine.format_rules_for_json(top_rules),
            'total': len(fpgrowth_engine.rules)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ROUTES DE RECOMMANDATION
# ============================================================================

@app.route('/api/recommend', methods=['POST'])
def get_recommendations():
    """Obtenir des recommandations basées sur des items"""
    try:
        if not app_state['analysis_done']:
            return jsonify({
                'success': False,
                'error': 'L\'analyse doit être effectuée d\'abord'
            }), 400
        
        # Récupérer les paramètres
        data = request.get_json()
        items = data.get('items', [])
        top_n = data.get('top_n', 5)
        min_confidence = data.get('min_confidence', 0.5)
        
        if not items:
            return jsonify({
                'success': False,
                'error': 'La liste d\'items ne peut pas être vide'
            }), 400
        
        # Obtenir les recommandations
        recommendations = recommender.recommend(items, top_n, min_confidence)
        
        # Sauvegarder dans la base de données
        if recommendations:
            for rec in recommendations:
                db.save_recommendation(
                    items,
                    [rec['item']],
                    rec['confidence']
                )
        
        return jsonify({
            'success': True,
            'input_items': items,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/frequently-bought-together', methods=['POST'])
def frequently_bought_together():
    """Trouver les items fréquemment achetés ensemble"""
    try:
        if not app_state['analysis_done']:
            return jsonify({
                'success': False,
                'error': 'L\'analyse doit être effectuée d\'abord'
            }), 400
        
        data = request.get_json()
        item = data.get('item')
        top_n = data.get('top_n', 5)
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Un item doit être fourni'
            }), 400
        
        together = recommender.get_frequently_bought_together(item, top_n)
        
        return jsonify({
            'success': True,
            'item': item,
            'frequently_bought_together': together,
            'count': len(together)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
        user_cart = data.get('cart', [])  # Nouveau: panier de l'utilisateur
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Le message ne peut pas être vide'
            }), 400
        
        # Récupérer TOUS les produits disponibles avec métadonnées
        available_products = None
        recommendations = None
        
        if app_state.get('data_loaded'):
            try:
                # Récupérer beaucoup plus de produits (top 200)
                top_products = data_loader.get_top_products(200)
                
                # Enrichir avec les métadonnées (prix, description)
                metadata = products_manager.get_all_products()
                products_with_info = []
                for name in top_products.keys():
                    product_meta = metadata.get(name, {})
                    price = product_meta.get('price', 0)
                    products_with_info.append(f"{name} ({price}€)")
                
                available_products = products_with_info
                
                # Si le panier n'est pas vide, obtenir des recommandations FP-Growth
                if user_cart and len(user_cart) > 0:
                    try:
                        cart_names = [item['name'] if isinstance(item, dict) else item for item in user_cart]
                        recs = data_loader.get_recommendations(cart_names, top_n=10)
                        if recs:
                            recommendations = [rec['product'] for rec in recs[:5]]
                    except:
                        pass
            except:
                pass
        
        response = llm_service.chatbot_response(
            user_message=user_message,
            conversation_history=conversation_history,
            available_products=available_products,
            user_cart=user_cart,
            fp_recommendations=recommendations
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

# ============================================================================
# POINT D'ENTRÉE
# ============================================================================


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Démarrage de l'API FP-Growth Recommender System")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 URL: http://localhost:5000")
    print(f"📚 Documentation: http://localhost:5000/api/info")
    print("=" * 60)
    
    # Tentative de chargement automatique au démarrage
    try:
        print("Initialisation: Vérification des données existantes...")
        df = data_loader.load_data()
        if df is not None and not df.empty:
            app_state['data_loaded'] = True
            print("✓ Données chargées automatiquement au démarrage")
    except Exception as e:
        print(f"Info: Aucune donnée chargée au démarrage ({e})")

    app.run(host='0.0.0.0', port=5000, debug=True)
