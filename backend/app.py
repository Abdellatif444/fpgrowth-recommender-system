"""
API Flask pour le système de recommandation FP-Growth
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from datetime import datetime

# Imports des modules locaux
from database import db
from data_loader import data_loader
from fpgrowth_engine import fpgrowth_engine
from recommender import recommender

# Initialisation de l'application Flask
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JSON_SORT_KEYS'] = False

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
# ROUTES DE GESTION DES DONNÉES
# ============================================================================

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Charger et nettoyer les données"""
    try:
        start_time = time.time()
        
        # Charger les données
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
            'elapsed_time': f'{elapsed_time:.2f}s'
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
