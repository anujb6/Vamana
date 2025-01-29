import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

symbol_df = pd.read_csv("../data/symbols/symbol_data.csv")
main_folder = "../data/monthly_data"

sector_dict = {}
for _, row in symbol_df.iterrows():
    sector = row['sector']
    company = row['name of company'].replace(' ', '_').lower()
    total_mcap = row['market cap']

    if sector not in sector_dict:
        sector_dict[sector] = []
    
    sector_dict[sector].append({
        'company': company,
        'market_cap': total_mcap
    })

def save_sector_chart(sector, price_df, save_path):
    plt.style.use('dark_background')
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    ax1.plot(price_df['date'], price_df['close'], color='#00ff00', linewidth=1.5)
    ax1.set_title(f'{sector} Sector Index', fontsize=14, pad=20)
    ax1.grid(True, alpha=0.2)
    ax1.set_ylabel('Price', fontsize=12)
    
    ax2.plot(price_df['date'], price_df['rsi'], color='#ff9900', linewidth=1.5)
    ax2.axhline(y=60, color='#ff0000', linestyle='--', alpha=0.5)
    ax2.axhline(y=40, color='#ffffff', linestyle='--', alpha=0.3)
    ax2.grid(True, alpha=0.2)
    ax2.set_ylabel('RSI', fontsize=12)
    ax2.set_ylim(0, 100)
    
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()

for sector, companies in sector_dict.items():
    all_dates = set()
    valid_companies = []
    company_data = []
    
    for company_info in companies:
        company = company_info['company']
        file_path = os.path.join(main_folder, company, f"{company}.csv")
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            
            if len(df) > 0:
                all_dates.update(df['date'].tolist())
                valid_companies.append(company_info)
                company_data.append(df)
    
    if valid_companies:
        date_range = pd.DataFrame({'date': sorted(list(all_dates))})
        date_range['date'] = pd.to_datetime(date_range['date'])
        total_mcap = sum(comp['market_cap'] for comp in valid_companies)
        
        sector_price_df = date_range.copy()
        sector_price_df['close'] = 0
        
        for i, company_info in enumerate(valid_companies):
            weight = company_info['market_cap'] / total_mcap
            df = company_data[i]
            
            company_prices = pd.merge(date_range, df[['date', 'close']], 
                                    on='date', how='left')
            company_prices['close'] = company_prices['close'].fillna(method='ffill')
            company_prices['close'] = company_prices['close'].fillna(method='bfill')
            
            sector_price_df['close'] += company_prices['close'] * weight
        
        delta = sector_price_df['close'].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        avg_gain = gain.ewm(span=14, adjust=False).mean()
        avg_loss = loss.ewm(span=14, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, np.nan) 
        sector_price_df['rsi'] = 100 - (100 / (1 + rs))
        sector_price_df['rsi'] = sector_price_df['rsi'].fillna(100)
        
        sector_dir = f'../data/sectors/{sector}'
        os.makedirs(sector_dir, exist_ok=True)
        
        sector_price_df.to_csv(f"{sector_dir}/{sector}_price.csv", index=False)
        
        chart_path = f"{sector_dir}/{sector}_chart.png"
        save_sector_chart(sector, sector_price_df, chart_path)
        
        print(f"Processed sector: {sector} - Chart saved at {chart_path}")