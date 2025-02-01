from data_loaders import monthly_data, rsi, symbol_data
from strategies import industrial_rsi, sectorial_rsi
nse_symbols_path = "data/symbols/equity_symbols.csv"

updated_symbols_path = 'data/symbols/symbol_data.csv'
start_date = '2010-01-01'
interval = '1mo'
end_date = '2025-01-31'

monthly_data_folder = "data/monthly_data"

# symbol_data.load(symbols_path=nse_symbols_path)
monthly_data.load(symbol_data_path=updated_symbols_path, start_date=start_date, end_date=end_date, interval=interval)
rsi.compute(main_folder=monthly_data_folder)

industrial_rsi.compute(main_folder=monthly_data_folder, symbol_data_path=updated_symbols_path)
sectorial_rsi.compute(main_folder=monthly_data_folder, symbol_data_path=updated_symbols_path)