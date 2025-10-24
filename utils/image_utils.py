import matplotlib.pyplot as plt

def store_image(path, df):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    ax1.plot(df['date'], df['close'], label='Close Price', color='blue')
    ax1.set_title('Stock Price and RSI')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid()

    ax2.plot(df['date'], df['rsi'], label='RSI (14)', color='orange')
    ax2.axhline(60, color='red', linestyle='--', label='Overbought (60)')
    ax2.axhline(40, color='green', linestyle='--', label='Oversold (40)')
    ax2.set_ylabel('RSI')
    ax2.set_xlabel('Date')
    ax2.legend()
    ax2.grid()

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(path, format='png', dpi=300)
    plt.close() 
