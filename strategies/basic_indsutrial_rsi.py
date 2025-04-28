import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def compute(main_folder, symbol_data_path):
    symbol_df = pd.read_csv(symbol_data_path)
    
    industry_dict = {}
    for _, row in symbol_df.iterrows():
        industry = row['basic industry']
        company = row['name of company'].replace(' ', '_').lower()
        total_mcap = row['market cap']
        
        if industry not in industry_dict:
            industry_dict[industry] = []
        industry_dict[industry].append({
            'company': company,
            'market_cap': total_mcap
        })

    def calculate_rsi(prices, period=14):
        """Calculate RSI for a price series"""
        if len(prices) <= period:
            return pd.Series(np.nan, index=prices.index)
            
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        rsi = rsi.fillna(100) 
        return rsi

    def save_interactive_chart(category, price_df, save_path, title):
        price_df.reset_index(inplace=True)
        price_df.set_index('date', inplace=True)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

        fig.add_trace(go.Candlestick(
            x=price_df.index,
            open=price_df['open'],
            high=price_df['high'],
            low=price_df['low'],
            close=price_df['close'],
            name='Price'
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=price_df.index,
            y=price_df['rsi'],
            mode='lines',
            name='RSI',
            line=dict(color='orange')
        ), row=2, col=1)

        fig.add_hline(y=60, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=40, line_dash="dash", line_color="green", row=2, col=1)

        fig.update_layout(
            title=title,
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=800
        )

        fig.write_html(save_path)
        print(f"Interactive chart saved at {save_path}")

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
            
            total_companies = len(valid_companies)
            weight = 1 / total_companies
            
            price_df = date_range.copy()
            price_df['open'] = 0.0
            price_df['high'] = 0.0
            price_df['low'] = 0.0
            price_df['close'] = 0.0
                        
            for i, company_info in enumerate(valid_companies):
                df = company_data[i]
                df = df[['date', 'open', 'high', 'low', 'close']]
                
                company_prices = pd.merge(date_range, df, on='date', how='left')
                
                company_prices[['open', 'high', 'low', 'close']] = company_prices[['open', 'high', 'low', 'close']].fillna(method='ffill').fillna(method='bfill')
                
                if company_prices['close'].iloc[0] == 0:
                    continue
                
                price_df['open'] += company_prices['open'] * weight
                price_df['high'] += company_prices['high'] * weight
                price_df['low'] += company_prices['low'] * weight
                price_df['close'] += company_prices['close'] * weight
            
            price_df['rsi'] = calculate_rsi(price_df['close'])
            
            price_df.set_index('date', inplace=True)
            monthly_price_df = price_df.resample('ME').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'rsi': 'last'  
            })
            
            if len(monthly_price_df) <= 14:
                print(f"Warning: Basic Industry {industry} has insufficient data for reliable RSI calculation")
            
            industry_formatted = industry.replace(' ', '_').replace('/', '-').lower()
            industry_dir = f'data/basic_industries/{industry_formatted}'
            os.makedirs(industry_dir, exist_ok=True)
            monthly_price_df.to_csv(f"{industry_dir}/{industry_formatted}_price.csv")
            chart_path = f"{industry_dir}/{industry_formatted}_chart.html"
            save_interactive_chart(industry_formatted, monthly_price_df, chart_path, f'{industry_formatted} Basic Industry Index - Monthly')
            print(f"Processed basic industry: {industry_formatted} - Chart saved at {chart_path}")