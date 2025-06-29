#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[ ]:


import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv("segmented_customers.csv")

app = dash.Dash(__name__)

# Bar chart of customer counts per segment
segment_counts = df["Segment"].value_counts().reset_index()
segment_counts.columns = ["Segment", "Count"]
bar_fig = px.bar(segment_counts, x="Segment", y="Count", title="Number of Customers per Segment")

# Pie chart of segment distribution
pie_fig = px.pie(segment_counts, names="Segment", values="Count", title="Segment Distribution")

# Scatter plot of age vs. spending score
scatter_fig = px.scatter(
    df,
    x="Age",
    y="Spending Score (1-100)",
    color="Segment",
    hover_data=["CustomerID", "Annual Income (k$)"],
    title="Age vs Spending Score by Segment"
)

# Bar chart of average income by segment
income_by_segment = df.groupby("Segment")["Annual Income (k$)"].mean().reset_index()
income_fig = px.bar(
    income_by_segment,
    x="Segment",
    y="Annual Income (k$)",
    title="Average Annual Income by Segment"
)

# Layout
app.layout = html.Div(children=[
    html.H1("Customer Segmentation Dashboard", style={"textAlign": "center"}),

    html.Div([
        html.H2("Segment Distribution"),
        dcc.Graph(figure=bar_fig),
        dcc.Graph(figure=pie_fig)
    ]),

    html.Div([
        html.H2("Age vs Spending Score"),
        dcc.Graph(figure=scatter_fig)
    ]),

    html.Div([
        html.H2("Average Income by Segment"),
        dcc.Graph(figure=income_fig)
    ])
])

if __name__ == "__main__":
    app.run(debug=True, port=8051)



# In[ ]:




