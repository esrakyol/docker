import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name="BIPM", count=count)

@app.route('/titanic')
def titanic():
    df = pd.read_csv('titanic.csv')
    table = df.head().to_html(classes='table')
    survivors = df.groupby('Sex')['Survived'].sum()
    female = int(survivors['female'])
    male = int(survivors['male'])
    chart = '<svg width="400" height="300">'
    chart += '<text x="200" y="20" text-anchor="middle" font-size="16">Survivors by Gender</text>'
    chart += f'<rect x="50" y="{300 - female * 2}" width="100" height="{female * 2}" fill="pink"/>'
    chart += f'<text x="100" y="295" text-anchor="middle">Female ({female})</text>'
    chart += f'<rect x="200" y="{300 - male * 2}" width="100" height="{male * 2}" fill="steelblue"/>'
    chart += f'<text x="250" y="295" text-anchor="middle">Male ({male})</text>'
    chart += '</svg>'
    return render_template('titanic.html', table=table, chart=chart)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)