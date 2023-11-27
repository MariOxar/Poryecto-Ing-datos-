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
sql_query = """
   SELECT a.avaliability_365, a.stars, tv.room_type
FROM airbnb a
JOIN hospedaje ho ON a.id = ho.id
JOIN tipo_vivienda tv ON ho.room_type_id = tv.room_type_id;
"""

# Consulta SQL para la suma de calificaciones por intervalo de disponibilidad
sql_suma_calificaciones = """
SELECT
    CASE
        WHEN avaliability_365 <= 182 THEN '0-182'
        ELSE '183-365'
    END AS intervalo_disponibilidad,
    SUM(stars) AS suma_calificaciones
FROM
    Airbnb
GROUP BY
    intervalo_disponibilidad
ORDER BY
    intervalo_disponibilidad;
"""

sql_promedio_estrellas_tipo = """
SELECT t.room_type, AVG(a.stars) AS avg_rating
FROM Airbnb a
JOIN Hospedaje h ON a.id = h.id
JOIN Tipo_vivienda t ON h.room_type_id = t.room_type_id
GROUP BY t.room_type;
"""

# Consulta SQL para el promedio de disponibilidad por tipo de habitación
sql_promedio_disponibilidad_tipo = """
SELECT t.room_type, AVG(a.avaliability_365) AS avg_availability
FROM Airbnb a
JOIN Hospedaje h ON a.id = h.id
JOIN Tipo_vivienda t ON h.room_type_id = t.room_type_id
GROUP BY t.room_type;
"""

df = pd.read_sql(sql_query, conn)
df_suma_calificaciones = pd.read_sql(sql_suma_calificaciones, conn)

# Cerrar la conexión a la base de datos
conn.close()

# Crear intervalos de disponibilidad
disponibilidad_intervals = pd.cut(df['avaliability_365'], bins=[0, 182, 365], labels=['0-182', '183-365'])

# Agregar la columna de intervalos a los datos
df['disponibilidad_intervals'] = disponibilidad_intervals

# Calcular la calificación promedio por intervalo de disponibilidad
calificacion_promedio_por_intervalo = df.groupby('disponibilidad_intervals')['stars'].mean().reset_index()

# Calcular la suma de calificaciones por intervalo de disponibilidad
suma_calificaciones_intervalos = df_suma_calificaciones

# Calcular el promedio de disponibilidad por tipo de habitación
promedio_disponibilidad_por_tipo = df.groupby('room_type')['avaliability_365'].mean().reset_index()

# Calcular el promedio de estrellas por tipo de habitación
promedio_estrellas_por_tipo = df.groupby('room_type')['stars'].mean().reset_index()

# Crear la aplicación Dash
app = dash.Dash()

# Layout de la aplicación
app.layout = html.Div(style={'backgroundColor': '#FFFFFF', 'color': '#111111'}, children=[
    html.H1('Relación entre Disponibilidad y Calificación Promedio en Airbnb', style={
        'text-align': 'center',
        'color': '#111111'
    }),

    html.Div([
        dcc.Graph(
            id='bar-chart-promedio',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=calificacion_promedio_por_intervalo['disponibilidad_intervals'],
                        y=calificacion_promedio_por_intervalo['stars'],
                        name='Calificación Promedio',
                    ),
                ],
                layout=go.Layout(
                    title='Calificación Promedio por Intervalo de Disponibilidad',
                    xaxis={'title': 'Intervalo de Disponibilidad'},
                    yaxis={'title': 'Calificación Promedio'},
                    template='plotly_dark',
                )
            )
        ),
        dash_table.DataTable(
            id='table-calificacion-promedio',
            columns=[
                {'name': 'Intervalo de Disponibilidad', 'id': 'disponibilidad_intervals'},
                {'name': 'Calificación Promedio', 'id': 'stars'},
            ],
            data=calificacion_promedio_por_intervalo.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='bar-chart-suma',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=suma_calificaciones_intervalos['intervalo_disponibilidad'],
                        y=suma_calificaciones_intervalos['suma_calificaciones'],
                        name='Suma de Calificaciones',
                    ),
                ],
                layout=go.Layout(
                    title='Suma de Calificaciones por Intervalo de Disponibilidad',
                    xaxis={'title': 'Intervalo de Disponibilidad'},
                    yaxis={'title': 'Suma de Calificaciones'},
                    template='plotly_dark',
                )
            )
        ),
        dash_table.DataTable(
            id='table-suma-calificaciones',
            columns=[
                {'name': 'Intervalo de Disponibilidad', 'id': 'intervalo_disponibilidad'},
                {'name': 'Suma de Calificaciones', 'id': 'suma_calificaciones'},
            ],
            data=suma_calificaciones_intervalos.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),
    
    html.Div([
        dcc.Graph(
            id='bar-chart-promedio-tipo',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=promedio_disponibilidad_por_tipo['room_type'],
                        y=promedio_disponibilidad_por_tipo['avaliability_365'],
                        name='Promedio de Disponibilidad',
                    ),
                ],
                layout=go.Layout(
                    title='Promedio de Disponibilidad por Tipo de Habitación',
                    xaxis={'title': 'Tipo de Habitación'},
                    yaxis={'title': 'Promedio de Disponibilidad'},
                    template='plotly_dark',
                )
            )
        ),
        dash_table.DataTable(
            id='table-promedio-disponibilidad-tipo',
            columns=[
                {'name': 'Tipo de Habitación', 'id': 'room_type'},
                {'name': 'Promedio de Disponibilidad', 'id': 'avaliability_365'},
            ],
            data=promedio_disponibilidad_por_tipo.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),

    html.Div([
        dcc.Graph(
            id='bar-chart-promedio-estrellas-tipo',
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=promedio_estrellas_por_tipo['room_type'],
                        y=promedio_estrellas_por_tipo['stars'],
                        name='Promedio de Estrellas',
                    ),
                ],
                layout=go.Layout(
                    title='Promedio de Estrellas por Tipo de Habitación',
                    xaxis={'title': 'Tipo de Habitación'},
                    yaxis={'title': 'Promedio de Estrellas'},
                    template='plotly_dark',
                )
            )
        ),
        dash_table.DataTable(
            id='table-promedio-estrellas-tipo',
            columns=[
                {'name': 'Tipo de Habitación', 'id': 'room_type'},
                {'name': 'Promedio de Estrellas', 'id': 'stars'},
            ],
            data=promedio_estrellas_por_tipo.to_dict('records'),
            style_table={'height': '200px', 'overflowY': 'auto'},
        ),
    ]),
])

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8085)
