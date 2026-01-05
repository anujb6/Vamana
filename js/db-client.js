/**
 * Vamana Data Client - Static JSON API Version
 * Loads data on-demand from pre-built JSON files
 * Reduces initial load from 77MB to ~350KB
 */

class VamanaDataClient {
    constructor() {
        this.cache = new Map();
        this.isReady = false;
        this.data = {
            symbols: null,
            sectors: null,
            industries: null,
            basicIndustries: null,
            metadata: null
        };
    }

    /**
     * Initialize the client by loading metadata and indices
     */
    async init() {
        try {
            // Load core data in parallel for faster startup
            const [metadata, symbols, sectors, industries, basicIndustries] = await Promise.all([
                this.fetchJSON('data/api/metadata.json'),
                this.fetchJSON('data/api/symbols.json'),
                this.fetchJSON('data/api/sectors/index.json'),
                this.fetchJSON('data/api/industries/index.json'),
                this.fetchJSON('data/api/basic-industries/index.json')
            ]);

            this.data.metadata = metadata;
            this.data.symbols = symbols;
            this.data.sectors = sectors;
            this.data.industries = industries;
            this.data.basicIndustries = basicIndustries;

            this.isReady = true;
            console.log('VamanaDataClient initialized successfully');

            // Dispatch event for UI to know data is ready
            window.dispatchEvent(new Event('vamanaDataReady'));

            return true;
        } catch (error) {
            console.error('Failed to initialize VamanaDataClient:', error);
            throw error;
        }
    }

    /**
     * Fetch JSON with caching
     */
    async fetchJSON(url) {
        if (this.cache.has(url)) {
            return this.cache.get(url);
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${url}: ${response.status}`);
        }

        const data = await response.json();
        this.cache.set(url, data);
        return data;
    }

    // ==================== Symbol Queries ====================

    /**
     * Get all symbols with their metadata
     */
    async getSymbols() {
        if (!this.isReady) await this.init();
        return this.data.symbols;
    }

    /**
     * Get symbols by sector
     */
    async getSymbolsBySector(sector) {
        if (!this.isReady) await this.init();
        return this.data.symbols.filter(s => s.sector === sector);
    }

    /**
     * Get symbols by industry
     */
    async getSymbolsByIndustry(industry) {
        if (!this.isReady) await this.init();
        return this.data.symbols.filter(s => s.industry === industry);
    }

    /**
     * Get symbols by basic industry
     */
    async getSymbolsByBasicIndustry(basicIndustry) {
        if (!this.isReady) await this.init();
        return this.data.symbols.filter(s => s.basic_industry === basicIndustry);
    }

    // ==================== Sector Queries ====================

    /**
     * Get all unique sectors with company counts
     */
    async getSectors() {
        if (!this.isReady) await this.init();
        return this.data.sectors.map(s => ({
            sector: s.name,
            company_count: s.company_count
        }));
    }

    /**
     * Get latest RSI for all sectors
     */
    async getSectorsWithLatestRsi() {
        if (!this.isReady) await this.init();
        return this.data.sectors.map(s => ({
            sector: s.name,
            rsi: s.rsi,
            date: s.date,
            close: s.close,
            company_count: s.company_count
        }));
    }

    /**
     * Get sectors with RSI below threshold
     */
    async getSectorsByRsiBelow(threshold) {
        const sectors = await this.getSectorsWithLatestRsi();
        return sectors.filter(s => s.rsi !== null && s.rsi < threshold);
    }

    /**
     * Get sectors with RSI in range
     */
    async getSectorsByRsiRange(minRsi, maxRsi) {
        const sectors = await this.getSectorsWithLatestRsi();
        return sectors.filter(s => s.rsi !== null && s.rsi >= minRsi && s.rsi <= maxRsi);
    }

    /**
     * Get sectors with RSI above threshold
     */
    async getSectorsByRsiAbove(threshold) {
        const sectors = await this.getSectorsWithLatestRsi();
        return sectors.filter(s => s.rsi !== null && s.rsi >= threshold);
    }

    /**
     * Get price history for a sector (on-demand loading)
     */
    async getSectorPriceHistory(sector) {
        const sectorData = this.data.sectors.find(s => s.name === sector);
        if (!sectorData) return [];

        const url = `data/api/sectors/${sectorData.slug}.json`;
        return await this.fetchJSON(url);
    }

    // ==================== Industry Queries ====================

    /**
     * Get all unique industries with company counts
     */
    async getIndustries() {
        if (!this.isReady) await this.init();
        return this.data.industries.map(i => ({
            industry: i.name,
            company_count: i.company_count
        }));
    }

    /**
     * Get latest RSI for all industries
     */
    async getIndustriesWithLatestRsi() {
        if (!this.isReady) await this.init();
        return this.data.industries.map(i => ({
            industry: i.name,
            rsi: i.rsi,
            date: i.date,
            close: i.close,
            company_count: i.company_count
        }));
    }

    /**
     * Get industries with RSI below threshold
     */
    async getIndustriesByRsiBelow(threshold) {
        const industries = await this.getIndustriesWithLatestRsi();
        return industries.filter(i => i.rsi !== null && i.rsi < threshold);
    }

    /**
     * Get industries with RSI in range
     */
    async getIndustriesByRsiRange(minRsi, maxRsi) {
        const industries = await this.getIndustriesWithLatestRsi();
        return industries.filter(i => i.rsi !== null && i.rsi >= minRsi && i.rsi <= maxRsi);
    }

    /**
     * Get industries with RSI above threshold
     */
    async getIndustriesByRsiAbove(threshold) {
        const industries = await this.getIndustriesWithLatestRsi();
        return industries.filter(i => i.rsi !== null && i.rsi >= threshold);
    }

    /**
     * Get price history for an industry (on-demand loading)
     */
    async getIndustryPriceHistory(industry) {
        const industryData = this.data.industries.find(i => i.name === industry);
        if (!industryData) return [];

        const url = `data/api/industries/${industryData.slug}.json`;
        return await this.fetchJSON(url);
    }

    // ==================== Basic Industry Queries ====================

    /**
     * Get all unique basic industries with company counts
     */
    async getBasicIndustries() {
        if (!this.isReady) await this.init();
        return this.data.basicIndustries.map(bi => ({
            basic_industry: bi.name,
            company_count: bi.company_count
        }));
    }

    /**
     * Get latest RSI for all basic industries
     */
    async getBasicIndustriesWithLatestRsi() {
        if (!this.isReady) await this.init();
        return this.data.basicIndustries.map(bi => ({
            basic_industry: bi.name,
            rsi: bi.rsi,
            date: bi.date,
            close: bi.close,
            company_count: bi.company_count
        }));
    }

    /**
     * Get basic industries with RSI below threshold
     */
    async getBasicIndustriesByRsiBelow(threshold) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        return basicIndustries.filter(bi => bi.rsi !== null && bi.rsi < threshold);
    }

    /**
     * Get basic industries with RSI in range
     */
    async getBasicIndustriesByRsiRange(minRsi, maxRsi) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        return basicIndustries.filter(bi => bi.rsi !== null && bi.rsi >= minRsi && bi.rsi <= maxRsi);
    }

    /**
     * Get basic industries with RSI above threshold
     */
    async getBasicIndustriesByRsiAbove(threshold) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        return basicIndustries.filter(bi => bi.rsi !== null && bi.rsi >= threshold);
    }

    /**
     * Get price history for a basic industry (on-demand loading)
     */
    async getBasicIndustryPriceHistory(basicIndustry) {
        const biData = this.data.basicIndustries.find(bi => bi.name === basicIndustry);
        if (!biData) return [];

        const url = `data/api/basic-industries/${biData.slug}.json`;
        return await this.fetchJSON(url);
    }

    // ==================== Combined RSI Queries ====================

    /**
     * Get all categories (sectors, industries, basic industries) with RSI below threshold
     */
    async getAllCategoriesByRsiBelow(threshold) {
        const [sectors, industries, basicIndustries] = await Promise.all([
            this.getSectorsByRsiBelow(threshold),
            this.getIndustriesByRsiBelow(threshold),
            this.getBasicIndustriesByRsiBelow(threshold)
        ]);

        const results = [];
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.sector,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.industry,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));
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
        const [sectors, industries, basicIndustries] = await Promise.all([
            this.getSectorsByRsiRange(minRsi, maxRsi),
            this.getIndustriesByRsiRange(minRsi, maxRsi),
            this.getBasicIndustriesByRsiRange(minRsi, maxRsi)
        ]);

        const results = [];
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.sector,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.industry,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));
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
        const [sectors, industries, basicIndustries] = await Promise.all([
            this.getSectorsByRsiAbove(threshold),
            this.getIndustriesByRsiAbove(threshold),
            this.getBasicIndustriesByRsiAbove(threshold)
        ]);

        const results = [];
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.sector,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.industry,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));
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
        if (!this.isReady) await this.init();
        return this.data.metadata;
    }

    /**
     * Get statistics
     */
    async getStats() {
        if (!this.isReady) await this.init();
        return {
            totalCompanies: this.data.metadata.total_companies,
            totalSectors: this.data.metadata.total_sectors,
            totalIndustries: this.data.metadata.total_industries,
            totalBasicIndustries: this.data.metadata.total_basic_industries
        };
    }
}

// Export for use in browser with backward compatible name
if (typeof window !== 'undefined') {
    window.VamanaDataClient = VamanaDataClient;
    window.VamanaDB = VamanaDataClient;  // Backward compatibility
}

// Export for ES modules
export { VamanaDataClient };
