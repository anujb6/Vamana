import pandas as pd
import plotly.express as px


df = pd.read_csv(r'')
fig = px.sunburst(
    df,
    path=['macro sector', 'sector', 'industry', 'basic industry', 'symbol'],  # Define the hierarchy
    values=None,  # We are not using a numeric value, just the hierarchy
    title="Hierarchical Visualization: Macro Sector -> Sector -> Industry -> Basic Industry",
    color='macro sector',  # Optional: Color by macro sector
)

# Show the plot
fig.show()