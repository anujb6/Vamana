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

    def save_interactive_chart(category, price_df, save_path, title):
        price_df.reset_index(inplace=True)  # Ensure 'date' is a column
        
        price_df.set_index('date', inplace=True)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])

        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=price_df.index,
            open=price_df['open'],
            high=price_df['high'],
            low=price_df['low'],
            close=price_df['close'],
            name='Price'
        ), row=1, col=1)

        # RSI chart
        fig.add_trace(go.Scatter(
            x=price_df.index,
            y=price_df['rsi'],
            mode='lines',
            name='RSI',
            line=dict(color='orange')
        ), row=2, col=1)

        # Add RSI threshold lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

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
            total_mcap = sum(comp['market_cap'] for comp in valid_companies)
            price_df = date_range.copy()
            price_df[['open', 'high', 'low', 'close']] = 0
            
            for i, company_info in enumerate(valid_companies):
                weight = company_info['market_cap'] / total_mcap
                df = company_data[i]
                df = df[['date', 'open', 'high', 'low', 'close']]
                
                company_prices = pd.merge(date_range, df, on='date', how='left')
                company_prices[['open', 'high', 'low', 'close']] = company_prices[['open', 'high', 'low', 'close']].fillna(method='ffill').fillna(method='bfill')
                price_df[['open', 'high', 'low', 'close']] += company_prices[['open', 'high', 'low', 'close']] * weight
            
            price_df.set_index('date', inplace=True)
            price_df = price_df.resample('ME').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})
            
            delta = price_df['close'].diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            avg_gain = gain.ewm(span=14, adjust=False).mean()
            avg_loss = loss.ewm(span=14, adjust=False).mean()
            rs = avg_gain / avg_loss.replace(0, np.nan)
            price_df['rsi'] = 100 - (100 / (1 + rs))
            price_df['rsi'] = price_df['rsi'].fillna(100)
            
            industry = industry.replace(' ', '_').replace('/', '-').lower()
            industry_dir = f'data/basic_industries/{industry}'
            os.makedirs(industry_dir, exist_ok=True)
            price_df.to_csv(f"{industry_dir}/{industry}_price.csv")
            chart_path = f"{industry_dir}/{industry}_chart.html"
            save_interactive_chart(industry, price_df, chart_path, f'{industry} Industry Index - Monthly')
            print(f"Processed industry: {industry} - Chart saved at {chart_path}")
