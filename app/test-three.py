import plotly.graph_objects as go


mapbox_access_token = 'pk.eyJ1IjoiY3NzbnIiLCJhIjoiY2xneDcwdXRuMDJwYjNmcXM1MTB1dGx3aiJ9.MQOT4EifvfaJJPvE2G6jNQ'

fig = go.Figure(go.Scattermapbox(
        lat=['45.5017'],
        lon=['-73.5673'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=14
        ),
        text=['Montreal'],
    ))

fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=go.layout.mapbox.Center(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5
    )
)

fig.show()
