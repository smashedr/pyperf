import plotly.express as px
import pandas as pd

# df = pd.DataFrame(dict(
#     x=[1, 2, 3, 4],
#     y=[5, 4, 5, 4],
# ))

df = {
    'x': [1, 2, 3, 4],
    'y': [5, 4, 5, 4],
}

# df = df.sort_values(by="x")
fig = px.line(df, x="x", y="y", title="Sorted Input", markers=True, line_shape='spline')
fig.show()
