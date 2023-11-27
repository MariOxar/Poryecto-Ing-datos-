import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import dash_table
import psycopg2 as psy2

# Configuración de la conexión a la base de datos
dbname = "Airbnb"
user = "Pruebas"
password = "123456"
host = "localhost"

# Establecer conexión a la base de datos
conn = psy2.connect(dbname=dbname, user=user, password=password, host=host)

# Consulta SQL para obtener datos relevantes 

sql_query_hospedajes = """
   SELECT neighbourhood, COUNT(*) AS cantidad_hospedajes
FROM Hospedaje
GROUP BY neighbourhood;
"""

sql_query_airbnb = """
   SELECT a.avaliability_365, a.stars, tv.room_type, h.price, h.neighbourhood
FROM airbnb a
JOIN hospedaje h ON a.id = h.id
JOIN tipo_vivienda tv ON h.room_type_id = tv.room_type_id;
"""

sql_query_suma_precio = """
   SELECT neighbourhood,
       sum(price) AS precio_suma
FROM Hospedaje
GROUP BY neighbourhood;
"""

sql_query_entire_home = """
   SELECT neighbourhood,
       COUNT(*) AS total_entire_home
FROM Hospedaje h
JOIN Tipo_vivienda tv ON h.room_type_id = tv.room_type_id
WHERE tv.room_type = 'Entire home/apt'
GROUP BY neighbourhood;
"""

sql_query_private_room = """
   SELECT neighbourhood,
       COUNT(*) AS total_private_room
FROM Hospedaje h
JOIN Tipo_vivienda tv ON h.room_type_id = tv.room_type_id
WHERE tv.room_type = 'Private room'
GROUP BY neighbourhood;
"""
sql_query_shared_room = """
SELECT neighbourhood,
       COUNT(*) AS total_shared_room
FROM Hospedaje h
JOIN Tipo_vivienda tv ON h.room_type_id = tv.room_type_id
WHERE tv.room_type = 'Shared room'
GROUP BY neighbourhood;
"""

df_hospedajes = pd.read_sql(sql_query_hospedajes, conn)
df_airbnb = pd.read_sql(sql_query_airbnb, conn)
df_suma_precio = pd.read_sql(sql_query_suma_precio, conn)
df_entire_home = pd.read_sql(sql_query_entire_home, conn)
df_private_room = pd.read_sql(sql_query_private_room, conn)
df_shared_room = pd.read_sql(sql_query_shared_room, conn)

# Redondear el precio promedio al entero más cercano
df_airbnb['precio_entero'] = round(df_airbnb['price'])

# Calcular el promedio de precios enteros por tipo de habitación
promedio_precios_enteros_por_tipo = df_airbnb.groupby('room_type')['precio_entero'].mean().reset_index()

# Calcular la cantidad de hospedajes por vecindario
cantidad_hospedajes_por_vecindario = df_hospedajes.groupby('neighbourhood')['cantidad_hospedajes'].sum().reset_index()

# Crear la aplicación Dash
app = dash.Dash()

# Layout de la aplicación
app.layout = html.Div(style={'backgroundColor': '#FFFFFF', 'color': '#111111'}, children=[
    html.H1('Análisis de cantidad hospedaje por vecindario', style={
        'text-align': 'center',
        'color': '#111111'
    }),

    html.Div([
        dcc.Graph(
            id='bar-chart-promedio-precio-entero-tipo',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=promedio_precios_enteros_por_tipo['room_type'],
                        y=promedio_precios_enteros_por_tipo['precio_entero'],
                        name='Promedio de Precio (Entero)',
                    ),
                ],
                layout=go.Layout(
                    title='Promedio de Precio (Entero) por Tipo de Habitación',
                    xaxis={'title': 'Tipo de Habitación'},
                    yaxis={'title': 'Promedio de Precio'},
                    template='plotly_dark',
                    bargap=0.1,  # Ajusta este valor para controlar el espacio entre las barras
                )
            )
        ),
        dash_table.DataTable(
            id='table-promedio-precio-entero-tipo',
            columns=[
                {'name': 'Tipo de Habitación', 'id': 'room_type'},
                {'name': 'Promedio de Precio (Entero)', 'id': 'precio_entero', 'type': 'numeric', 'format': dict(specifier=',.0f')},
            ],
            data=promedio_precios_enteros_por_tipo.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='bar-chart-cantidad-hospedajes-vecindario',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=cantidad_hospedajes_por_vecindario['neighbourhood'],
                        y=cantidad_hospedajes_por_vecindario['cantidad_hospedajes'],
                        name='Cantidad de Hospedajes',
                    ),
                ],
                layout=go.Layout(
                    title='Cantidad de Hospedajes por Vecindario',
                    xaxis={'title': 'Vecindario'},
                    yaxis={'title': 'Cantidad de Hospedajes'},
                    template='plotly_dark',
                    bargap=0.008,  # Ajusta este valor para controlar el espacio entre las barras
                )
            )
        ),
        dash_table.DataTable(
            id='table-cantidad-hospedajes-vecindario',
            columns=[
                {'name': 'Vecindario', 'id': 'neighbourhood'},
                {'name': 'Cantidad de Hospedajes', 'id': 'cantidad_hospedajes'},
            ],
            data=cantidad_hospedajes_por_vecindario.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),
    
    html.Div([
        dcc.Graph(
            id='bar-chart-suma-precio-vecindario',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=df_suma_precio['neighbourhood'],
                        y=df_suma_precio['precio_suma'],
                        name='Suma de Precio',
                    ),
                ],
                layout=go.Layout(
                    title='Suma de Precio de Hospedajes por Vecindario',
                    xaxis={'title': 'Vecindario'},
                    yaxis={'title': 'Suma de Precio'},
                    template='plotly_dark',
                    bargap=0.1,  # Ajusta este valor para controlar el espacio entre las barras
                )
            )
        ),
        dash_table.DataTable(
            id='table-suma-precio-vecindario',
            columns=[
                {'name': 'Vecindario', 'id': 'neighbourhood'},
                {'name': 'Suma de Precio', 'id': 'precio_suma'},
            ],
            data=df_suma_precio.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='bar-chart-total-entire-home-vecindario',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=df_entire_home['neighbourhood'],
                        y=df_entire_home['total_entire_home'],
                        name='Total Entire Home/Apt',
                    ),
                ],
                layout=go.Layout(
                    title='Total de "Entire Home/Apt" por Vecindario',
                    xaxis={'title': 'Vecindario'},
                    yaxis={'title': 'Total Entire Home/Apt'},
                    template='plotly_dark',
                    bargap=0.1,  # Ajusta este valor para controlar el espacio entre las barras
                )
            )
        ),
        dash_table.DataTable(
            id='table-total-entire-home-vecindario',
            columns=[
                {'name': 'Vecindario', 'id': 'neighbourhood'},
                {'name': 'Total Entire Home/Apt', 'id': 'total_entire_home'},
            ],
            data=df_entire_home.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='bar-chart-total-private-room-vecindario',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=df_private_room['neighbourhood'],
                        y=df_private_room['total_private_room'],
                        name='Total Private Room',
                    ),
                ],
                layout=go.Layout(
                    title='Total de "Private Room" por Vecindario',
                    xaxis={'title': 'Vecindario'},
                    yaxis={'title': 'Total Private Room'},
                    template='plotly_dark',
                    bargap=0.1,  # Ajusta este valor para controlar el espacio entre las barras
                )
            )
        ),
        dash_table.DataTable(
            id='table-total-private-room-vecindario',
            columns=[
                {'name': 'Vecindario', 'id': 'neighbourhood'},
                {'name': 'Total Private Room', 'id': 'total_private_room'},
            ],
            data=df_private_room.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),
    
    html.Div([
        dcc.Graph(
            id='bar-chart-total-shared-room-vecindario',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=df_shared_room['neighbourhood'],
                        y=df_shared_room['total_shared_room'],
                        name='Total Shared Room',
                    ),
                ],
                layout=go.Layout(
                    title='Total de "Shared Room" por Vecindario',
                    xaxis={'title': 'Vecindario'},
                    yaxis={'title': 'Total Shared Room'},
                    template='plotly_dark',
                    bargap=0.1,  # Ajusta este valor para controlar el espacio entre las barras
                )
            )
        ),
        dash_table.DataTable(
            id='table-total-shared-room-vecindario',
            columns=[
                {'name': 'Vecindario', 'id': 'neighbourhood'},
                {'name': 'Total Shared Room', 'id': 'total_shared_room'},
            ],
            data=df_shared_room.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),
])

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8085)
