from flask import Flask, render_template
from flask_sockets import Sockets

from master import Master
from utils.grapher import MultiGraph

import thread, time, json
import datetime

app = Flask(__name__)
sockets = Sockets(app)

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
m = Master()

test = {
    "graphs": [{
        "id": "#redis",
        "series": [
            {
                "name": "test",
                "data": [
                    [datetime.datetime.now(), 5],
                ]
            }
        ]
    }]
}

def get_stats():
    test = {"graphs": []}

    for stat in m.graphs.stats:
        print "Graphing %s" % stat.name
        data = {
            'id': stat.name,
            'series': []
        }
        if isinstance(stat, MultiGraph):
            print stat.graphs
            data['series'] = [{"name": k, "data": v} for k, v in stat.graph("week", start=datetime.datetime.now()).items()]
        else:
            if not stat.parent: continue
            data['series'] = [{"name": stat.name, "data": stat.graph("week", start=datetime.datetime.now())}]

        test['graphs'].append(data)
    return json.dumps(test, default=dthandler)


@sockets.route('/socket')
def socket(ws):
    while True:
        data = get_stats()
        ws.send(data)
        time.sleep(15)  # This value should change depending on how much load you want on your redis-db

@app.route('/')
def hello():
    m.update()
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

