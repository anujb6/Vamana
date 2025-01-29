import pandas as pd
import plotly.express as px


df = pd.read_csv(r'')
fig = px.sunburst(
    df,
    path=['sector', 'industry', 'basic industry', 'symbol'],
    values=None,
    title="Hierarchical Visualization: Sector -> Industry -> Basic Industry",
)

# Show the plot
fig.show()