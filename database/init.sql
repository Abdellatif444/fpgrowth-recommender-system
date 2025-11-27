-- Initialisation de la base de données FP-Growth

-- Table des transactions
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    invoice_no VARCHAR(50) NOT NULL,
    stock_code VARCHAR(50) NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP NOT NULL,
    unit_price DECIMAL(10, 2),
    customer_id VARCHAR(50),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour améliorer les performances
CREATE INDEX idx_invoice_no ON transactions(invoice_no);
CREATE INDEX idx_customer_id ON transactions(customer_id);
CREATE INDEX idx_invoice_date ON transactions(invoice_date);
CREATE INDEX idx_stock_code ON transactions(stock_code);

-- Table des itemsets fréquents
CREATE TABLE IF NOT EXISTS frequent_itemsets (
    id SERIAL PRIMARY KEY,
    itemset TEXT NOT NULL,
    support DECIMAL(10, 6) NOT NULL,
    length INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des règles d'association
CREATE TABLE IF NOT EXISTS association_rules (
    id SERIAL PRIMARY KEY,
    antecedent TEXT NOT NULL,
    consequent TEXT NOT NULL,
    support DECIMAL(10, 6) NOT NULL,
    confidence DECIMAL(10, 6) NOT NULL,
    lift DECIMAL(10, 6) NOT NULL,
    leverage DECIMAL(10, 6),
    conviction DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les règles
CREATE INDEX idx_confidence ON association_rules(confidence DESC);
CREATE INDEX idx_lift ON association_rules(lift DESC);

-- Table des recommandations générées
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    input_items TEXT NOT NULL,
    recommended_items TEXT NOT NULL,
    confidence DECIMAL(10, 6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vue pour les statistiques
CREATE OR REPLACE VIEW stats_view AS
SELECT 
    COUNT(DISTINCT invoice_no) as total_invoices,
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT stock_code) as total_products,
    COUNT(*) as total_transactions,
    AVG(quantity) as avg_quantity,
    AVG(unit_price) as avg_price
FROM transactions;

-- Fonction pour nettoyer les anciennes analyses
CREATE OR REPLACE FUNCTION clean_old_analysis() RETURNS void AS $$
BEGIN
    DELETE FROM frequent_itemsets WHERE created_at < NOW() - INTERVAL '7 days';
    DELETE FROM association_rules WHERE created_at < NOW() - INTERVAL '7 days';
    DELETE FROM recommendations WHERE created_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données FP-Growth initialisée avec succès!';
END $$;
