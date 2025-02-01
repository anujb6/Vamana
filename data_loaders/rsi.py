import os
import glob
import pandas as pd
import talib as ta
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from utils.image_utils import store_image

def compute(main_folder):
    for subfolder in os.listdir(main_folder):
        subfolder_path = os.path.join(main_folder, subfolder)

        if os.path.isdir(subfolder_path):
            csv_files = glob.glob(os.path.join(subfolder_path, "*.csv"))
            
            if csv_files:
                csv_file = csv_files[0] 
                df = pd.read_csv(csv_file)
                df['date'] = pd.to_datetime(df['date'])
                df['rsi'] = ta.RSI(df['close'], timeperiod=14)
                df.to_csv(csv_file)
                store_image(csv_file.replace('.csv', '.png'), df)
                print(f"Processd file: {csv_file}")