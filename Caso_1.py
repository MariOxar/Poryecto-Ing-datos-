import dash
from dash import dcc as dcc
from dash import html as html
import pandas as pd
import psycopg2 as psy2

db = "Airbnb"
user = "Pruebas"
password = "123456"
host = "Localhost"

con = psy2.connect(dbname=db, user=user, password=password, host=host)


app = dash.Dash(__name__)

cursor = con.cursor()

query = "select neighbourhood, COUNT(*) n_veces from datos GROUP BY neighbourhood ORDER BY n_veces DESC"

cursor.execute(query)

data = cursor.fetchall()


cursor2 = con.cursor()
consulta = "SELECT neighbourhood, AVG(stars) AS promedio_stars FROM datos GROUP BY neighbourhood"
cursor2.execute(consulta)
data2 = cursor2.fetchall()


app.layout = html.Div([
    dcc.Graph(
        id='repetition-graph',
        figure={
            'data': [{'x': [row[0]], 'y': [row[1]],'type': 'bar'} for row in data],
            'layout': {
                'title': 'Numero de datos dentro del barrio segun neighbourhood'
            }
        }
    ),
    dcc.Graph(
        id='repetition-graph',
        figure={
            'data': [{'x': [row[0]], 'y': [row[1]],'type': 'bar'} for row in data2],
            'layout': {
                'title': 'Promedio de estrellas segun neighbourhood'
            }
        }
    ),
    html.P("En la primera grafica se puede observar los vecindarios (neighbourhood) que tienen mas airbnbs ubicados en esa zona. En la segunda grafica se puede ver los ratings promedio que tienen esos vecindarios en promedio."
           "a pesar de que no se pueda ver la ubicacion de los vecindarios dado que los vecindarios estan en un codigo unico por lo que no se puede observar como tal por zona pero se puede ver que las reseñas estan por encima"
           "de 4 estrellas muy cerca a 5 sin importar la cantidad de lugares que queden en ese vecindario y se puede ver que para algunos lugares tener tantos airbnbs en la zona igualmente muestran un numero promedio de"
           "estrellas muy alto entonces se puede ver que en general los ratings son altos y no afecta mucho la zona o los vecindarios en los ratings altos. Los ratings van desde 4.75 hasta 4.9 que son todos ratings muy altos."
           " Siendo el rating mas alto el de un vecindarion que solo tiene 64 ubicaciones. Y el vecindario que tiene menos ubicaciones dentro de ella es una que tiene 7 airbnbs en ella, con un rating promedio 4.81.")

])

if __name__ == '__main__':
    app.run_server(debug=True)


con.close()

