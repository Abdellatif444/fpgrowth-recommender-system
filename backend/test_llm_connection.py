"""
Script de test pour vérifier la connexion LLM Gateway
"""
import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer le service LLM
sys.path.append(os.path.dirname(__file__))
from llm_service import llm_service

def test_llm_connection():
    """Test de connexion LLM Gateway"""
    print("=" * 60)
    print("🧪 TEST DE CONNEXION LLM GATEWAY")
    print("=" * 60)
    
    # Vérifier que la clé API est configurée
    api_key = os.getenv('LLMGATEWAY_API_KEY')
    if not api_key:
        print("❌ ERREUR: Clé API non trouvée dans .env")
        return False
    
    print(f"✅ Clé API trouvée: {api_key[:20]}...")
    
    # Test 1: Explication simple
    print("\n📝 Test 1: Explication de recommandation")
    print("-" * 60)
    
    explanation = llm_service.explain_recommendation(
        basket_items=["WHITE HANGING HEART T-LIGHT HOLDER"],
        recommended_item="REGENCY CAKESTAND 3 TIER",
        confidence=0.65,
        lift=3.2
    )
    
    print(f"Résultat: {explanation}")
    
    if "Erreur" in explanation or "LLM non configuré" in explanation:
        print("❌ Test échoué")
        return False
    else:
        print("✅ Test réussi")
    
    # Test 2: Détection de contexte
    print("\n🔍 Test 2: Détection de contexte")
    print("-" * 60)
    
    context = llm_service.detect_shopping_context([
        "WHITE HANGING HEART T-LIGHT HOLDER",
        "PARTY BUNTING",
        "REGENCY CAKESTAND 3 TIER"
    ])
    
    print(f"Contexte détecté: {context.get('context', 'N/A')}")
    print(f"Style: {context.get('style', 'N/A')}")
    print(f"Suggestions: {', '.join(context.get('suggestions', []))}")
    
    if context.get('context') == "Non détecté":
        print("❌ Test échoué")
        return False
    else:
        print("✅ Test réussi")
    
    # Test 3: Chatbot
    print("\n💬 Test 3: Chatbot")
    print("-" * 60)
    
    response = llm_service.chatbot_response(
        user_message="Bonjour, je cherche des décorations pour une fête",
        available_products=["WHITE HANGING HEART", "PARTY BUNTING", "REGENCY CAKESTAND"]
    )
    
    print(f"Réponse: {response}")
    
    if "Erreur" in response:
        print("❌ Test échoué")
        return False
    else:
        print("✅ Test réussi")
    
    # Résumé final
    print("\n" + "=" * 60)
    print("🎉 TOUS LES TESTS SONT PASSÉS !")
    print("=" * 60)
    print("\n✅ L'intégration LLM Gateway est fonctionnelle")
    print("✅ Vous pouvez maintenant utiliser les fonctionnalités IA")
    print("\nProchaines étapes:")
    print("  1. Redémarrer le backend: docker-compose restart backend")
    print("  2. Intégrer les endpoints dans app.py")
    print("  3. Ajouter l'interface frontend")
    
    return True

if __name__ == "__main__":
    try:
        success = test_llm_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
