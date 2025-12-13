/**
 * Vamana Database Client
 * Uses sql.js to query SQLite database in browser
 */

class VamanaDB {
    constructor() {
        this.db = null;
        this.isReady = false;
    }

    /**
     * Initialize the database connection
     * @param {string} dbUrl - URL to the SQLite database file
     */
    async init(dbUrl = 'data/vamana.db') {
        try {
            // Initialize sql.js (loaded via script tag)
            const SQL = await initSqlJs({
                locateFile: file => `https://sql.js.org/dist/${file}`
            });

            // Fetch the database file
            const response = await fetch(dbUrl);
            if (!response.ok) {
                throw new Error(`Failed to fetch database: ${response.status}`);
            }
            const arrayBuffer = await response.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);

            // Create the database from the file
            this.db = new SQL.Database(uint8Array);
            this.isReady = true;
            console.log('VamanaDB initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize VamanaDB:', error);
            throw error;
        }
    }

    /**
     * Execute a SQL query
     * @param {string} sql - SQL query string
     * @param {Array} params - Query parameters
     * @returns {Promise<Array>} Query results as array of objects
     */
    async query(sql, params = []) {
        if (!this.isReady) {
            throw new Error('Database not initialized. Call init() first.');
        }

        // Use prepared statement for parameter binding
        const stmt = this.db.prepare(sql);
        if (params.length > 0) {
            stmt.bind(params);
        }

        const results = [];
        while (stmt.step()) {
            const row = stmt.getAsObject();
            results.push(row);
        }
        stmt.free();

        return results;
    }

    // ==================== Symbol Queries ====================

    /**
     * Get all symbols with their metadata
     */
    async getSymbols() {
        return await this.query(`
            SELECT symbol, name_of_company, macro_sector, sector,
                   industry, basic_industry, market_cap
            FROM symbols
            ORDER BY name_of_company
        `);
    }

    /**
     * Get symbols by sector
     */
    async getSymbolsBySector(sector) {
        return await this.query(`
            SELECT symbol, name_of_company, market_cap
            FROM symbols
            WHERE sector = ?
            ORDER BY name_of_company
        `, [sector]);
    }

    /**
     * Get symbols by industry
     */
    async getSymbolsByIndustry(industry) {
        return await this.query(`
            SELECT symbol, name_of_company, market_cap
            FROM symbols
            WHERE industry = ?
            ORDER BY name_of_company
        `, [industry]);
    }

    /**
     * Get symbols by basic industry
     */
    async getSymbolsByBasicIndustry(basicIndustry) {
        return await this.query(`
            SELECT symbol, name_of_company, market_cap
            FROM symbols
            WHERE basic_industry = ?
            ORDER BY name_of_company
        `, [basicIndustry]);
    }

    // ==================== Sector Queries ====================

    /**
     * Get all unique sectors with company counts
     */
    async getSectors() {
        return await this.query(`
            SELECT sector, COUNT(*) as company_count
            FROM symbols
            WHERE sector IS NOT NULL AND sector != ''
            GROUP BY sector
            ORDER BY sector
        `);
    }

    /**
     * Get latest RSI for all sectors
     */
    async getSectorsWithLatestRsi() {
        return await this.query(`
            SELECT sp.sector, sp.rsi, sp.date, sp.close,
                   (SELECT COUNT(*) FROM symbols s WHERE s.sector = sp.sector) as company_count
            FROM sector_prices sp
            WHERE sp.date = (
                SELECT MAX(date) FROM sector_prices WHERE sector = sp.sector
            )
            ORDER BY sp.sector
        `);
    }

    /**
     * Get sectors with RSI below threshold
     */
    async getSectorsByRsiBelow(threshold) {
        return await this.query(`
            SELECT sp.sector, sp.rsi, sp.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.sector = sp.sector) as company_count
            FROM sector_prices sp
            WHERE sp.date = (
                SELECT MAX(date) FROM sector_prices WHERE sector = sp.sector
            )
            AND sp.rsi < ?
            ORDER BY sp.rsi
        `, [threshold]);
    }

    /**
     * Get sectors with RSI in range
     */
    async getSectorsByRsiRange(minRsi, maxRsi) {
        return await this.query(`
            SELECT sp.sector, sp.rsi, sp.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.sector = sp.sector) as company_count
            FROM sector_prices sp
            WHERE sp.date = (
                SELECT MAX(date) FROM sector_prices WHERE sector = sp.sector
            )
            AND sp.rsi >= ? AND sp.rsi <= ?
            ORDER BY sp.rsi
        `, [minRsi, maxRsi]);
    }

    /**
     * Get sectors with RSI above threshold
     */
    async getSectorsByRsiAbove(threshold) {
        return await this.query(`
            SELECT sp.sector, sp.rsi, sp.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.sector = sp.sector) as company_count
            FROM sector_prices sp
            WHERE sp.date = (
                SELECT MAX(date) FROM sector_prices WHERE sector = sp.sector
            )
            AND sp.rsi >= ?
            ORDER BY sp.rsi DESC
        `, [threshold]);
    }

    /**
     * Get price history for a sector
     */
    async getSectorPriceHistory(sector) {
        return await this.query(`
            SELECT date, open, high, low, close, rsi
            FROM sector_prices
            WHERE sector = ?
            ORDER BY date
        `, [sector]);
    }

    // ==================== Industry Queries ====================

    /**
     * Get all unique industries with company counts
     */
    async getIndustries() {
        return await this.query(`
            SELECT industry, COUNT(*) as company_count
            FROM symbols
            WHERE industry IS NOT NULL AND industry != ''
            GROUP BY industry
            ORDER BY industry
        `);
    }

    /**
     * Get latest RSI for all industries
     */
    async getIndustriesWithLatestRsi() {
        return await this.query(`
            SELECT ip.industry, ip.rsi, ip.date, ip.close,
                   (SELECT COUNT(*) FROM symbols s WHERE s.industry = ip.industry) as company_count
            FROM industry_prices ip
            WHERE ip.date = (
                SELECT MAX(date) FROM industry_prices WHERE industry = ip.industry
            )
            ORDER BY ip.industry
        `);
    }

    /**
     * Get industries with RSI below threshold
     */
    async getIndustriesByRsiBelow(threshold) {
        return await this.query(`
            SELECT ip.industry, ip.rsi, ip.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.industry = ip.industry) as company_count
            FROM industry_prices ip
            WHERE ip.date = (
                SELECT MAX(date) FROM industry_prices WHERE industry = ip.industry
            )
            AND ip.rsi < ?
            ORDER BY ip.rsi
        `, [threshold]);
    }

    /**
     * Get industries with RSI in range
     */
    async getIndustriesByRsiRange(minRsi, maxRsi) {
        return await this.query(`
            SELECT ip.industry, ip.rsi, ip.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.industry = ip.industry) as company_count
            FROM industry_prices ip
            WHERE ip.date = (
                SELECT MAX(date) FROM industry_prices WHERE industry = ip.industry
            )
            AND ip.rsi >= ? AND ip.rsi <= ?
            ORDER BY ip.rsi
        `, [minRsi, maxRsi]);
    }

    /**
     * Get industries with RSI above threshold
     */
    async getIndustriesByRsiAbove(threshold) {
        return await this.query(`
            SELECT ip.industry, ip.rsi, ip.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.industry = ip.industry) as company_count
            FROM industry_prices ip
            WHERE ip.date = (
                SELECT MAX(date) FROM industry_prices WHERE industry = ip.industry
            )
            AND ip.rsi >= ?
            ORDER BY ip.rsi DESC
        `, [threshold]);
    }

    /**
     * Get price history for an industry
     */
    async getIndustryPriceHistory(industry) {
        return await this.query(`
            SELECT date, open, high, low, close, rsi
            FROM industry_prices
            WHERE industry = ?
            ORDER BY date
        `, [industry]);
    }

    // ==================== Basic Industry Queries ====================

    /**
     * Get all unique basic industries with company counts
     */
    async getBasicIndustries() {
        return await this.query(`
            SELECT basic_industry, COUNT(*) as company_count
            FROM symbols
            WHERE basic_industry IS NOT NULL AND basic_industry != ''
            GROUP BY basic_industry
            ORDER BY basic_industry
        `);
    }

    /**
     * Get latest RSI for all basic industries
     */
    async getBasicIndustriesWithLatestRsi() {
        return await this.query(`
            SELECT bip.basic_industry, bip.rsi, bip.date, bip.close,
                   (SELECT COUNT(*) FROM symbols s WHERE s.basic_industry = bip.basic_industry) as company_count
            FROM basic_industry_prices bip
            WHERE bip.date = (
                SELECT MAX(date) FROM basic_industry_prices WHERE basic_industry = bip.basic_industry
            )
            ORDER BY bip.basic_industry
        `);
    }

    /**
     * Get basic industries with RSI below threshold
     */
    async getBasicIndustriesByRsiBelow(threshold) {
        return await this.query(`
            SELECT bip.basic_industry, bip.rsi, bip.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.basic_industry = bip.basic_industry) as company_count
            FROM basic_industry_prices bip
            WHERE bip.date = (
                SELECT MAX(date) FROM basic_industry_prices WHERE basic_industry = bip.basic_industry
            )
            AND bip.rsi < ?
            ORDER BY bip.rsi
        `, [threshold]);
    }

    /**
     * Get basic industries with RSI in range
     */
    async getBasicIndustriesByRsiRange(minRsi, maxRsi) {
        return await this.query(`
            SELECT bip.basic_industry, bip.rsi, bip.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.basic_industry = bip.basic_industry) as company_count
            FROM basic_industry_prices bip
            WHERE bip.date = (
                SELECT MAX(date) FROM basic_industry_prices WHERE basic_industry = bip.basic_industry
            )
            AND bip.rsi >= ? AND bip.rsi <= ?
            ORDER BY bip.rsi
        `, [minRsi, maxRsi]);
    }

    /**
     * Get basic industries with RSI above threshold
     */
    async getBasicIndustriesByRsiAbove(threshold) {
        return await this.query(`
            SELECT bip.basic_industry, bip.rsi, bip.date,
                   (SELECT COUNT(*) FROM symbols s WHERE s.basic_industry = bip.basic_industry) as company_count
            FROM basic_industry_prices bip
            WHERE bip.date = (
                SELECT MAX(date) FROM basic_industry_prices WHERE basic_industry = bip.basic_industry
            )
            AND bip.rsi >= ?
            ORDER BY bip.rsi DESC
        `, [threshold]);
    }

    /**
     * Get price history for a basic industry
     */
    async getBasicIndustryPriceHistory(basicIndustry) {
        return await this.query(`
            SELECT date, open, high, low, close, rsi
            FROM basic_industry_prices
            WHERE basic_industry = ?
            ORDER BY date
        `, [basicIndustry]);
    }

    // ==================== Combined RSI Queries ====================

    /**
     * Get all categories (sectors, industries, basic industries) with RSI below threshold
     */
    async getAllCategoriesByRsiBelow(threshold) {
        const results = [];

        // Sectors
        const sectors = await this.getSectorsByRsiBelow(threshold);
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.sector,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));

        // Industries
        const industries = await this.getIndustriesByRsiBelow(threshold);
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.industry,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));

        // Basic Industries
        const basicIndustries = await this.getBasicIndustriesByRsiBelow(threshold);
        basicIndustries.forEach(bi => results.push({
            type: 'Basic Industries',
            category: bi.basic_industry,
            rsi: bi.rsi,
            date: bi.date,
            company_count: bi.company_count
        }));

        return results;
    }

    /**
     * Get all categories with RSI in range
     */
    async getAllCategoriesByRsiRange(minRsi, maxRsi) {
        const results = [];

        const sectors = await this.getSectorsByRsiRange(minRsi, maxRsi);
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.sector,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));

        const industries = await this.getIndustriesByRsiRange(minRsi, maxRsi);
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.industry,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));

        const basicIndustries = await this.getBasicIndustriesByRsiRange(minRsi, maxRsi);
        basicIndustries.forEach(bi => results.push({
            type: 'Basic Industries',
            category: bi.basic_industry,
            rsi: bi.rsi,
            date: bi.date,
            company_count: bi.company_count
        }));

        return results;
    }

    /**
     * Get all categories with RSI above threshold
     */
    async getAllCategoriesByRsiAbove(threshold) {
        const results = [];

        const sectors = await this.getSectorsByRsiAbove(threshold);
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.sector,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));

        const industries = await this.getIndustriesByRsiAbove(threshold);
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.industry,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));

        const basicIndustries = await this.getBasicIndustriesByRsiAbove(threshold);
        basicIndustries.forEach(bi => results.push({
            type: 'Basic Industries',
            category: bi.basic_industry,
            rsi: bi.rsi,
            date: bi.date,
            company_count: bi.company_count
        }));

        return results;
    }

    // ==================== Metadata Queries ====================

    /**
     * Get database metadata
     */
    async getMetadata() {
        const results = await this.query('SELECT key, value FROM metadata');
        const metadata = {};
        results.forEach(row => {
            metadata[row.key] = row.value;
        });
        return metadata;
    }

    /**
     * Get statistics
     */
    async getStats() {
        const [symbols] = await this.query('SELECT COUNT(*) as count FROM symbols');
        const [sectors] = await this.query('SELECT COUNT(DISTINCT sector) as count FROM symbols WHERE sector IS NOT NULL');
        const [industries] = await this.query('SELECT COUNT(DISTINCT industry) as count FROM symbols WHERE industry IS NOT NULL');
        const [basicIndustries] = await this.query('SELECT COUNT(DISTINCT basic_industry) as count FROM symbols WHERE basic_industry IS NOT NULL');

        return {
            totalCompanies: symbols.count,
            totalSectors: sectors.count,
            totalIndustries: industries.count,
            totalBasicIndustries: basicIndustries.count
        };
    }
}

// Export for use in browser
if (typeof window !== 'undefined') {
    window.VamanaDB = VamanaDB;
}

// Export for ES modules
export { VamanaDB };
