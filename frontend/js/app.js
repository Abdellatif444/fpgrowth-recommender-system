/**
 * Application JavaScript pour FP-Growth Recommender System
 * Auteurs: Student A, Student Y
 */

// Configuration
const API_URL = 'http://localhost:5000/api';

// État de l'application
const appState = {
    dataLoaded: false,
    analysisComplete: false,
    currentTab: 'itemsets'
};

// ============================================================================
// UTILITAIRES
// ============================================================================

/**
 * Afficher/masquer l'overlay de chargement
 */
function toggleLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

/**
 * Afficher une notification toast
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * Mettre à jour le badge de statut
 */
function updateStatusBadge(text, color = '#10b981') {
    const badge = document.getElementById('statusBadge');
    const dot = badge.querySelector('.status-dot');
    const span = badge.querySelector('span:last-child');
    
    span.textContent = text;
    dot.style.background = color;
}

/**
 * Formater un nombre avec séparateurs de milliers
 */
function formatNumber(num) {
    return new Intl.NumberFormat('fr-FR').format(num);
}

/**
 * Formater un pourcentage
 */
function formatPercent(num) {
    return `${(num * 100).toFixed(2)}%`;
}

// ============================================================================
// API CALLS
// ============================================================================

/**
 * Appel API générique
 */
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erreur API');
        }
        
        return result;
    } catch (error) {
        console.error('Erreur API:', error);
        throw error;
    }
}

/**
 * Charger les données
 */
async function loadData() {
    toggleLoading(true);
    updateStatusBadge('Chargement des données...', '#f59e0b');
    
    try {
        const result = await apiCall('/load-data', 'POST');
        
        if (result.success) {
            appState.dataLoaded = true;
            updateHeroStats(result.stats);
            updateStatusBadge('Données chargées', '#10b981');
            showToast('Données chargées avec succès!', 'success');
            document.getElementById('analyzeBtn').disabled = false;
        }
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
        updateStatusBadge('Erreur', '#ef4444');
    } finally {
        toggleLoading(false);
    }
}

/**
 * Supprimer les données
 */
async function deleteData() {
    if (!confirm('Êtes-vous sûr de vouloir supprimer toutes les données ? Cette action est irréversible.')) {
        return;
    }

    toggleLoading(true);
    updateStatusBadge('Suppression...', '#ef4444');

    try {
        const result = await apiCall('/clear-data', 'POST');
        
        if (result.success) {
            appState.dataLoaded = false;
            appState.analysisComplete = false;
            
            // Réinitialiser l'interface
            updateHeroStats({
                total_invoices: '-',
                total_products: '-',
                total_customers: '-'
            });
            document.getElementById('resultsSection').style.display = 'none';
            document.getElementById('analyzeBtn').disabled = true;
            
            updateStatusBadge('Données supprimées', '#ef4444');
            showToast('Toutes les données ont été supprimées', 'success');
        }
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
        updateStatusBadge('Erreur', '#ef4444');
    } finally {
        toggleLoading(false);
    }
}

/**
 * Lancer l'analyse FP-Growth
 */
async function analyzeData() {
    const minSupport = parseFloat(document.getElementById('minSupport').value);
    const minConfidence = parseFloat(document.getElementById('minConfidence').value);
    
    toggleLoading(true);
    updateStatusBadge('Analyse en cours...', '#f59e0b');
    
    try {
        const result = await apiCall('/analyze', 'POST', {
            min_support: minSupport,
            min_confidence: minConfidence
        });
        
        if (result.success) {
            appState.analysisComplete = true;
            displayAnalysisStats(result.stats);
            await loadItemsets();
            await loadRules();
            updateStatusBadge('Analyse terminée', '#10b981');
            showToast(`Analyse terminée en ${result.elapsed_time}`, 'success');
            document.getElementById('resultsSection').style.display = 'block';
        }
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
        updateStatusBadge('Erreur', '#ef4444');
    } finally {
        toggleLoading(false);
    }
}

/**
 * Charger les itemsets fréquents
 */
async function loadItemsets() {
    try {
        const result = await apiCall('/itemsets?top_n=20&min_length=2');
        
        if (result.success) {
            displayItemsets(result.itemsets);
        }
    } catch (error) {
        showToast(`Erreur lors du chargement des itemsets: ${error.message}`, 'error');
    }
}

/**
 * Charger les règles d'association
 */
async function loadRules() {
    try {
        const result = await apiCall('/rules?top_n=20&min_lift=1.0');
        
        if (result.success) {
            displayRules(result.rules);
        }
    } catch (error) {
        showToast(`Erreur lors du chargement des règles: ${error.message}`, 'error');
    }
}

/**
 * Obtenir des recommandations
 */
async function getRecommendations() {
    const basketInput = document.getElementById('basketInput').value.trim();
    
    if (!basketInput) {
        showToast('Veuillez entrer des produits', 'error');
        return;
    }
    
    const items = basketInput.split(',').map(item => item.trim()).filter(item => item);
    
    toggleLoading(true);
    
    try {
        const result = await apiCall('/recommend', 'POST', {
            items: items,
            top_n: 10,
            min_confidence: 0.3
        });
        
        if (result.success) {
            displayRecommendations(result.recommendations, result.input_items);
            showToast(`${result.count} recommandations trouvées`, 'success');
        }
    } catch (error) {
        showToast(`Erreur: ${error.message}`, 'error');
    } finally {
        toggleLoading(false);
    }
}

// ============================================================================
// AFFICHAGE DES RÉSULTATS
// ============================================================================

/**
 * Mettre à jour les statistiques du hero
 */
function updateHeroStats(stats) {
    const statsDiv = document.getElementById('heroStats');
    statsDiv.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.total_invoices)}</div>
            <div class="stat-label">Transactions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.total_products)}</div>
            <div class="stat-label">Produits</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.total_customers)}</div>
            <div class="stat-label">Clients</div>
        </div>
    `;
}

/**
 * Afficher les statistiques de l'analyse
 */
function displayAnalysisStats(stats) {
    const statsDiv = document.getElementById('analysisStats');
    statsDiv.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.total_itemsets)}</div>
            <div class="stat-label">Itemsets Fréquents</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatNumber(stats.total_rules)}</div>
            <div class="stat-label">Règles d'Association</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${formatPercent(stats.avg_confidence)}</div>
            <div class="stat-label">Confiance Moyenne</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${stats.avg_lift.toFixed(2)}</div>
            <div class="stat-label">Lift Moyen</div>
        </div>
    `;
}

/**
 * Afficher les itemsets fréquents
 */
function displayItemsets(itemsets) {
    const container = document.getElementById('itemsetsList');
    
    if (!itemsets || itemsets.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">Aucun itemset trouvé</p>';
        return;
    }
    
    container.innerHTML = itemsets.map((itemset, index) => `
        <div class="result-item">
            <div class="result-header">
                <div class="result-items">
                    <strong>#${index + 1}</strong> ${itemset.items.join(' + ')}
                </div>
            </div>
            <div class="result-metrics">
                <div class="metric">
                    <div class="metric-label">Support</div>
                    <div class="metric-value">${formatPercent(itemset.support)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Longueur</div>
                    <div class="metric-value">${itemset.length}</div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Afficher les règles d'association
 */
function displayRules(rules) {
    const container = document.getElementById('rulesList');
    
    if (!rules || rules.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted);">Aucune règle trouvée</p>';
        return;
    }
    
    container.innerHTML = rules.map((rule, index) => `
        <div class="result-item">
            <div class="result-header">
                <div class="result-items">
                    <strong>#${index + 1}</strong> 
                    ${rule.antecedents.join(' + ')} 
                    <span style="color: var(--accent-color);">→</span> 
                    ${rule.consequents.join(' + ')}
                </div>
            </div>
            <div class="result-metrics">
                <div class="metric">
                    <div class="metric-label">Support</div>
                    <div class="metric-value">${formatPercent(rule.support)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Confiance</div>
                    <div class="metric-value">${formatPercent(rule.confidence)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Lift</div>
                    <div class="metric-value">${rule.lift.toFixed(2)}</div>
                </div>
            </div>
        </div>
    `).join('');
}

/**
 * Afficher les recommandations
 */
/**
 * Afficher les recommandations
 */
function displayRecommendations(recommendations, inputItems) {
    const container = document.getElementById('recommendationsList');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div style="padding: var(--spacing-lg); text-align: center; color: var(--text-muted);">
                <p>Aucune recommandation trouvée pour ces produits.</p>
                <p style="font-size: 0.875rem; margin-top: var(--spacing-sm);">
                    Essayez avec d'autres produits ou réduisez la confiance minimum.
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div style="margin-bottom: var(--spacing-md); padding: var(--spacing-md); background: var(--bg-secondary); border-radius: var(--radius-md);">
            <strong>Panier actuel:</strong> ${inputItems.join(', ')}
        </div>
        ${recommendations.map((rec, index) => `
            <div class="result-item">
                <div class="result-header">
                    <div class="result-items">
                        <strong>#${index + 1}</strong> ${rec.item}
                        <button class="btn-explain" onclick="explainRecommendation(this, ['${inputItems.join("','")}'], '${rec.item.replace(/'/g, "\\'")}', ${rec.confidence}, ${rec.lift})">
                            ✨ Expliquer
                        </button>
                    </div>
                </div>
                <div class="result-metrics">
                    <div class="metric">
                        <div class="metric-label">Confiance</div>
                        <div class="metric-value">${formatPercent(rec.confidence)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Lift</div>
                        <div class="metric-value">${rec.lift.toFixed(2)}</div>
                    </div>
                </div>
                <div style="margin-top: var(--spacing-xs); font-size: 0.875rem; color: var(--text-muted);">
                    Basé sur: ${rec.based_on.join(', ')}
                </div>
            </div>
        `).join('')}
    `;
    
    // Lancer la détection de contexte
    detectContext(inputItems);
}

// ============================================================================
// GESTION DES ONGLETS
// ============================================================================

function switchTab(tabName) {
    // Mettre à jour les boutons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Mettre à jour les panneaux
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    appState.currentTab = tabName;
}

// ============================================================================
// FONCTIONNALITÉS LLM (IA GÉNÉRATIVE)
// ============================================================================

/**
 * Basculer l'affichage du chatbot
 */
function toggleChatbot() {
    const window = document.getElementById('chatbotWindow');
    window.classList.toggle('active');
    
    // Focus sur l'input si ouvert
    if (window.classList.contains('active')) {
        document.getElementById('chatInput').focus();
    }
}

/**
 * Ajouter un message au chat
 */
function addMessageToChat(message, sender) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = message;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

/**
 * Envoyer un message au chatbot
 */
async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Afficher le message utilisateur
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Indicateur de frappe
    const loadingId = 'chat-loading-' + Date.now();
    const container = document.getElementById('chatMessages');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message bot';
    loadingDiv.id = loadingId;
    loadingDiv.textContent = '...';
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;
    
    try {
        // Récupérer l'historique (simplifié)
        const history = [];
        document.querySelectorAll('.message').forEach(el => {
            if (el.id !== loadingId) {
                history.push({
                    role: el.classList.contains('user') ? 'user' : 'assistant',
                    content: el.textContent
                });
            }
        });
        
        const result = await apiCall('/llm/chatbot', 'POST', {
            message: message,
            history: history.slice(-10) // Garder les 10 derniers messages
        });
        
        // Supprimer l'indicateur de chargement
        document.getElementById(loadingId).remove();
        
        if (result.success) {
            addMessageToChat(result.response, 'bot');
        } else {
            addMessageToChat("Désolé, j'ai rencontré une erreur.", 'bot');
        }
    } catch (error) {
        document.getElementById(loadingId).remove();
        addMessageToChat("Erreur de connexion au service IA.", 'bot');
        console.error(error);
    }
}

/**
 * Expliquer une recommandation
 */
async function explainRecommendation(btn, basketItems, recommendedItem, confidence, lift) {
    const resultItem = btn.closest('.result-item');
    
    // Vérifier si l'explication existe déjà
    let explanationBox = resultItem.querySelector('.explanation-box');
    if (explanationBox) {
        explanationBox.classList.toggle('active');
        return;
    }
    
    // Créer la boîte d'explication
    explanationBox = document.createElement('div');
    explanationBox.className = 'explanation-box';
    explanationBox.innerHTML = '<em>Génération de l\'explication par l\'IA...</em>';
    resultItem.appendChild(explanationBox);
    explanationBox.classList.add('active');
    
    // Désactiver le bouton pendant le chargement
    btn.disabled = true;
    btn.style.cursor = 'wait';
    
    try {
        const result = await apiCall('/llm/explain-recommendation', 'POST', {
            basket_items: basketItems,
            recommended_item: recommendedItem,
            confidence: confidence,
            lift: lift
        });
        
        if (result.success) {
            explanationBox.innerHTML = `<strong>💡 Analyse IA :</strong> ${result.explanation}`;
        } else {
            explanationBox.innerHTML = "Impossible de générer l'explication.";
        }
    } catch (error) {
        explanationBox.innerHTML = "Erreur lors de la communication avec l'IA.";
    } finally {
        btn.disabled = false;
        btn.style.cursor = 'pointer';
    }
}

/**
 * Détecter le contexte du panier
 */
async function detectContext(items) {
    const container = document.getElementById('recommendationsList');
    const contextDiv = document.createElement('div');
    contextDiv.id = 'contextAnalysis';
    contextDiv.style.marginBottom = '1rem';
    contextDiv.innerHTML = '<small>🤖 Analyse du contexte en cours...</small>';
    
    // Insérer après le résumé du panier
    const basketSummary = container.querySelector('div:first-child');
    basketSummary.parentNode.insertBefore(contextDiv, basketSummary.nextSibling);
    
    try {
        const result = await apiCall('/llm/detect-context', 'POST', {
            basket_items: items
        });
        
        if (result.success && result.context) {
            const ctx = result.context;
            contextDiv.innerHTML = `
                <div style="background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 8px; border: 1px solid var(--secondary-color);">
                    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 5px;">
                        <span class="context-badge">Contexte : ${ctx.context}</span>
                        <span class="context-badge" style="background: var(--primary-color);">Style : ${ctx.style}</span>
                    </div>
                    ${ctx.suggestions && ctx.suggestions.length > 0 ? 
                        `<div style="font-size: 0.9rem; color: var(--text-secondary);">
                            <strong>Suggestions IA :</strong> ${ctx.suggestions.join(', ')}
                        </div>` : ''}
                </div>
            `;
        } else {
            contextDiv.remove();
        }
    } catch (error) {
        console.error("Erreur contexte:", error);
        contextDiv.remove();
    }
}

// ============================================================================
// INITIALISATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 FP-Growth Recommender System initialisé');
    
    // Ouvrir le chatbot par défaut pour le montrer à l'utilisateur
    setTimeout(() => {
        const chatWindow = document.getElementById('chatbotWindow');
        if (!chatWindow.classList.contains('active')) {
            toggleChatbot();
        }
    }, 1000);
    
    // Event listeners pour les boutons
    document.getElementById('loadDataBtn').addEventListener('click', loadData);
    document.getElementById('deleteDataBtn').addEventListener('click', deleteData);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeData);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeData);
    document.getElementById('getRecommendationsBtn').addEventListener('click', getRecommendations);
    
    // Event listeners pour le Chatbot
    document.getElementById('chatbotToggle').addEventListener('click', toggleChatbot);
    document.getElementById('closeChat').addEventListener('click', toggleChatbot);
    document.getElementById('sendMessageBtn').addEventListener('click', sendChatMessage);
    document.getElementById('chatInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatMessage();
    });
    
    // Event listeners pour les onglets
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.dataset.tab);
        });
    });
    
    // Vérifier l'état de l'API et des données
    apiCall('/health')
        .then(async result => {
            updateStatusBadge('API connectée', '#10b981');
            console.log('✓ API connectée:', result);
            
            // Vérifier si des données sont déjà chargées
            try {
                const statsResult = await apiCall('/stats');
                if (statsResult.success && statsResult.stats.total_transactions > 0) {
                    console.log('✓ Données déjà présentes en mémoire');
                    appState.dataLoaded = true;
                    updateHeroStats(statsResult.stats);
                    updateStatusBadge('Données prêtes', '#10b981');
                    document.getElementById('analyzeBtn').disabled = false;
                    showToast('Données récupérées de la session précédente', 'success');
                }
            } catch (e) {
                console.log('Pas de données chargées initialement');
            }
        })
        .catch(error => {
            updateStatusBadge('API déconnectée', '#ef4444');
            showToast('Impossible de se connecter à l\'API', 'error');
            console.error('✗ Erreur de connexion:', error);
        });
});
