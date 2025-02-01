import pandas as pd
import plotly.express as px


df = pd.read_csv('../data/symbols/symbol_data.csv')
fig = px.sunburst(
    df,
    path=['sector', 'industry', 'basic industry', 'symbol'],
    values=None,
    title="Hierarchical Visualization: Sector -> Industry -> Basic Industry",
)

# Show the plot
fig.show()