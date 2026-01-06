/**
 * Vamana Data Client - Fetches data from static JSON API
 * Optimized for GitHub Pages hosting
 */

class VamanaDataClient {
    constructor() {
        this.cache = new Map();
        this.apiBase = 'data/api';
    }

    /**
     * Initialize the client by loading metadata
     */
    async init() {
        try {
            const metadata = await this.fetchJSON(`${this.apiBase}/metadata.json`);
            this.cache.set('metadata', metadata);
            console.log('VamanaDataClient initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize VamanaDataClient:', error);
            throw error;
        }
    }

    /**
     * Fetch a JSON file with caching
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
        return await this.fetchJSON(`${this.apiBase}/symbols.json`);
    }

    /**
     * Get symbols by sector
     */
    async getSymbolsBySector(sector) {
        const symbols = await this.getSymbols();
        return symbols.filter(s => s.sector === sector);
    }

    /**
     * Get symbols by industry
     */
    async getSymbolsByIndustry(industry) {
        const symbols = await this.getSymbols();
        return symbols.filter(s => s.industry === industry);
    }

    /**
     * Get symbols by basic industry
     */
    async getSymbolsByBasicIndustry(basicIndustry) {
        const symbols = await this.getSymbols();
        return symbols.filter(s => s.basic_industry === basicIndustry);
    }

    // ==================== Sector Queries ====================

    /**
     * Get all unique sectors with company counts
     */
    async getSectors() {
        const data = await this.fetchJSON(`${this.apiBase}/sectors/index.json`);
        return data.map(s => ({
            sector: s.name,
            company_count: s.company_count
        }));
    }

    /**
     * Get latest RSI for all sectors
     */
    async getSectorsWithLatestRsi() {
        return await this.fetchJSON(`${this.apiBase}/sectors/index.json`);
    }

    /**
     * Get sectors with RSI below threshold
     */
    async getSectorsByRsiBelow(threshold) {
        const sectors = await this.getSectorsWithLatestRsi();
        return sectors.filter(s => s.rsi < threshold);
    }

    /**
     * Get sectors with RSI in range
     */
    async getSectorsByRsiRange(minRsi, maxRsi) {
        const sectors = await this.getSectorsWithLatestRsi();
        return sectors.filter(s => s.rsi >= minRsi && s.rsi <= maxRsi);
    }

    /**
     * Get sectors with RSI above threshold
     */
    async getSectorsByRsiAbove(threshold) {
        const sectors = await this.getSectorsWithLatestRsi();
        return sectors.filter(s => s.rsi >= threshold);
    }

    /**
     * Get price history for a sector
     */
    async getSectorPriceHistory(sector) {
        const sectors = await this.getSectorsWithLatestRsi();
        const sectorData = sectors.find(s => s.name === sector);
        if (!sectorData) {
            throw new Error(`Sector not found: ${sector}`);
        }
        return await this.fetchJSON(`${this.apiBase}/sectors/${sectorData.slug}.json`);
    }

    // ==================== Industry Queries ====================

    /**
     * Get all unique industries with company counts
     */
    async getIndustries() {
        const data = await this.fetchJSON(`${this.apiBase}/industries/index.json`);
        return data.map(i => ({
            industry: i.name,
            company_count: i.company_count
        }));
    }

    /**
     * Get latest RSI for all industries
     */
    async getIndustriesWithLatestRsi() {
        return await this.fetchJSON(`${this.apiBase}/industries/index.json`);
    }

    /**
     * Get industries with RSI below threshold
     */
    async getIndustriesByRsiBelow(threshold) {
        const industries = await this.getIndustriesWithLatestRsi();
        return industries.filter(i => i.rsi < threshold);
    }

    /**
     * Get industries with RSI in range
     */
    async getIndustriesByRsiRange(minRsi, maxRsi) {
        const industries = await this.getIndustriesWithLatestRsi();
        return industries.filter(i => i.rsi >= minRsi && i.rsi <= maxRsi);
    }

    /**
     * Get industries with RSI above threshold
     */
    async getIndustriesByRsiAbove(threshold) {
        const industries = await this.getIndustriesWithLatestRsi();
        return industries.filter(i => i.rsi >= threshold);
    }

    /**
     * Get price history for an industry
     */
    async getIndustryPriceHistory(industry) {
        const industries = await this.getIndustriesWithLatestRsi();
        const industryData = industries.find(i => i.name === industry);
        if (!industryData) {
            throw new Error(`Industry not found: ${industry}`);
        }
        return await this.fetchJSON(`${this.apiBase}/industries/${industryData.slug}.json`);
    }

    // ==================== Basic Industry Queries ====================

    /**
     * Get all unique basic industries with company counts
     */
    async getBasicIndustries() {
        const data = await this.fetchJSON(`${this.apiBase}/basic-industries/index.json`);
        return data.map(bi => ({
            basic_industry: bi.name,
            company_count: bi.company_count
        }));
    }

    /**
     * Get latest RSI for all basic industries
     */
    async getBasicIndustriesWithLatestRsi() {
        return await this.fetchJSON(`${this.apiBase}/basic-industries/index.json`);
    }

    /**
     * Get basic industries with RSI below threshold
     */
    async getBasicIndustriesByRsiBelow(threshold) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        return basicIndustries.filter(bi => bi.rsi < threshold);
    }

    /**
     * Get basic industries with RSI in range
     */
    async getBasicIndustriesByRsiRange(minRsi, maxRsi) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        return basicIndustries.filter(bi => bi.rsi >= minRsi && bi.rsi <= maxRsi);
    }

    /**
     * Get basic industries with RSI above threshold
     */
    async getBasicIndustriesByRsiAbove(threshold) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        return basicIndustries.filter(bi => bi.rsi >= threshold);
    }

    /**
     * Get price history for a basic industry
     */
    async getBasicIndustryPriceHistory(basicIndustry) {
        const basicIndustries = await this.getBasicIndustriesWithLatestRsi();
        const biData = basicIndustries.find(bi => bi.name === basicIndustry);
        if (!biData) {
            throw new Error(`Basic industry not found: ${basicIndustry}`);
        }
        return await this.fetchJSON(`${this.apiBase}/basic-industries/${biData.slug}.json`);
    }

    // ==================== Combined RSI Queries ====================

    /**
     * Get all categories (sectors, industries, basic industries) with RSI below threshold
     */
    async getAllCategoriesByRsiBelow(threshold) {
        const results = [];

        const sectors = await this.getSectorsByRsiBelow(threshold);
        sectors.forEach(s => results.push({
            type: 'Sectors',
            category: s.name,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));

        const industries = await this.getIndustriesByRsiBelow(threshold);
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.name,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));

        const basicIndustries = await this.getBasicIndustriesByRsiBelow(threshold);
        basicIndustries.forEach(bi => results.push({
            type: 'Basic Industries',
            category: bi.name,
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
            category: s.name,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));

        const industries = await this.getIndustriesByRsiRange(minRsi, maxRsi);
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.name,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));

        const basicIndustries = await this.getBasicIndustriesByRsiRange(minRsi, maxRsi);
        basicIndustries.forEach(bi => results.push({
            type: 'Basic Industries',
            category: bi.name,
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
            category: s.name,
            rsi: s.rsi,
            date: s.date,
            company_count: s.company_count
        }));

        const industries = await this.getIndustriesByRsiAbove(threshold);
        industries.forEach(i => results.push({
            type: 'Industries',
            category: i.name,
            rsi: i.rsi,
            date: i.date,
            company_count: i.company_count
        }));

        const basicIndustries = await this.getBasicIndustriesByRsiAbove(threshold);
        basicIndustries.forEach(bi => results.push({
            type: 'Basic Industries',
            category: bi.name,
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
        return await this.fetchJSON(`${this.apiBase}/metadata.json`);
    }

    /**
     * Get statistics
     */
    async getStats() {
        const metadata = await this.getMetadata();
        return {
            totalCompanies: metadata.total_companies,
            totalSectors: metadata.total_sectors,
            totalIndustries: metadata.total_industries,
            totalBasicIndustries: metadata.total_basic_industries
        };
    }
}

// Export for use in browser
if (typeof window !== 'undefined') {
    window.VamanaDataClient = VamanaDataClient;
    window.VamanaDB = VamanaDataClient; // Backward compatibility
}

// Export for ES modules
export { VamanaDataClient };
