import os
import json

from flask import Flask, g, render_template, Response, request
from cell_tree_manager import CellTreeManager

app = Flask(__name__)
app.config.from_object(__name__)

# load default config and override config from an environment variable
app.config.update(dict(
    CWD=os.getcwd(),
    PATH=os.environ['TLPY_PATH'] if os.environ['TLPY_PATH'] else 'untitled.tlpy'
))
app.config.from_envvar('TLPY_SETTINGS', silent=True)

ctm = CellTreeManager(app.config['PATH'])

@app.route('/')
def index():
    return render_template('index.html', path=ctm.path)


@app.route('/raw_notebook')
def raw_notebook():
    return Response(
        json.dumps(
            ctm.render(),
            sort_keys=True,
            indent=4,
            separators=(',', ': ')
        ),
        mimetype='text/event-stream'
    )


@app.route('/cell', methods=['GET', 'POST'])
def cell():
    if request.method == 'GET':
        cell_id = request.args.get('cellid')
        source = request.args.get('source')
        if cell_id in ctm.cells.keys():
            ctm.set_current_cell(cell_id)
        return Response(
            json.dumps(
                ctm.current_cell.render(),
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
            )
        )
    if request.method == 'POST':
        source = str(json.loads(request.data.decode())['source'])
        cell_id = str(json.loads(request.data.decode())['cell_id'])
        n_children = int(json.loads(request.data.decode())['n_children'])
        ctm.set_current_cell(cell_id)
        ctm.current_cell.update_from_string(source)
        ctm.execute(n_children)

        print('='*40)
        print(ctm.cells.keys())
        print('='*40)

        return Response(ctm.current_cell.cell_id)


if __name__ == '__main__':
    app.run(debug=True)
