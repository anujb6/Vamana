import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import mplfinance as mpf

def compute(main_folder, symbol_data_path):
    symbol_df = pd.read_csv(symbol_data_path)
    
    industry_dict = {}
    for _, row in symbol_df.iterrows():
        industry = row['industry']
        company = row['name of company'].replace(' ', '_').lower()
        total_mcap = row['market cap']
        
        if industry not in industry_dict:
            industry_dict[industry] = []
        
        industry_dict[industry].append({
            'company': company,
            'market_cap': total_mcap
        })

    def save_industry_chart(industry, price_df, save_path):
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), gridspec_kw={'height_ratios': [2, 1]})
        
        mpf.plot(price_df, type='candle', style='charles', ax=ax1, volume=False)
        ax1.set_title(f'{industry} Industry Index - Monthly', fontsize=14, pad=20)
        ax1.set_ylabel('Price')
        
        ax2.plot(price_df.index, price_df['rsi'], color='#ff9900', linewidth=1.5)
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(y=30, color='green', linestyle='--', alpha=0.5)
        ax2.set_ylabel('RSI')
        ax2.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    for industry, companies in industry_dict.items():
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
            industry_price_df = date_range.copy()
            industry_price_df[['open', 'high', 'low', 'close']] = 0
            
            for i, company_info in enumerate(valid_companies):
                weight = company_info['market_cap'] / total_mcap
                df = company_data[i]
                df = df[['date', 'open', 'high', 'low', 'close']]
                
                company_prices = pd.merge(date_range, df, on='date', how='left')
                company_prices[['open', 'high', 'low', 'close']] = company_prices[['open', 'high', 'low', 'close']].fillna(method='ffill').fillna(method='bfill')
                industry_price_df[['open', 'high', 'low', 'close']] += company_prices[['open', 'high', 'low', 'close']] * weight
            
            industry_price_df.set_index('date', inplace=True)
            industry_price_df = industry_price_df.resample('M').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
            
            delta = industry_price_df['close'].diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            avg_gain = gain.ewm(span=14, adjust=False).mean()
            avg_loss = loss.ewm(span=14, adjust=False).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            industry_price_df['rsi'] = 100 - (100 / (1 + rs))
            industry_price_df['rsi'] = industry_price_df['rsi'].fillna(100)
            
            industry_dir = f'data/industries/{industry}'
            os.makedirs(industry_dir, exist_ok=True)
            industry_price_df.to_csv(f"{industry_dir}/{industry}_price.csv")
            chart_path = f"{industry_dir}/{industry}_chart.png"
            save_industry_chart(industry, industry_price_df, chart_path)
            print(f"Processed industry: {industry} - Chart saved at {chart_path}")
