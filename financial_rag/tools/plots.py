import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot, iplot
import pandas as pd
from typing import List



def plot_bars(df: pd.DataFrame,
              bars: List[str],
              by: str):
    
    fig = make_subplots()

    for b in bars:
        trace = go.Bar(
        x=df[by],
        y=df[b],
        name=b)
        fig.add_trace(trace)

    fig['layout'].update(height = 600,
                     width = 800,
                     title = "")
    iplot(fig)