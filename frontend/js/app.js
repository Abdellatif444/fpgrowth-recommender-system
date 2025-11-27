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
// INITIALISATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 FP-Growth Recommender System initialisé');
    
    // Event listeners pour les boutons
    document.getElementById('loadDataBtn').addEventListener('click', loadData);
    document.getElementById('deleteDataBtn').addEventListener('click', deleteData);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeData);
    document.getElementById('analyzeBtn').addEventListener('click', analyzeData);
    document.getElementById('getRecommendationsBtn').addEventListener('click', getRecommendations);
    
    // Event listeners pour les onglets
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchTab(btn.dataset.tab);
        });
    });
    
    // Vérifier l'état de l'API
    apiCall('/health')
        .then(result => {
            updateStatusBadge('API connectée', '#10b981');
            console.log('✓ API connectée:', result);
        })
        .catch(error => {
            updateStatusBadge('API déconnectée', '#ef4444');
            showToast('Impossible de se connecter à l\'API', 'error');
            console.error('✗ Erreur de connexion:', error);
        });
});
