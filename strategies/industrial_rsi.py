import pandas as pd
import plotly.express as px

df = pd.read_csv(r'C:\Users\AnujBhor\Desktop\nosedive\data\symbols\symbol_data.csv')
fig = px.sunburst(
    df,
    path=['sector', 'industry', 'basic industry', 'symbol'],  # Define the hierarchy
    values=None,  # We are not using a numeric value, just the hierarchy
    title="Hierarchical Visualization: Sector -> Industry -> Basic Industry",
    # color='sector ',  # Optional: Color by macro sector
)

# Show the plot
fig.show()