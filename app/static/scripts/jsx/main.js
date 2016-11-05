var Textarea = require('react-textarea-autosize').default;

var Cell = React.createClass({

    getInitialState() {

        return {
            cell_id: this.props.cell_id,
            source: this.props.source,
            stdout: this.props.stdout,
            parent_id: this.props.parent_id,
            children_id: this.props.children_id
        }
    },

    // componentWillReceiveProps(nextProps) {
    //     this.setState({
    //         cell_id: nextProps.cell_id,
    //         source: nextProps.source,
    //         stdout: nextProps.stdout,
    //         parent_id: nextProps.parent_id,
    //         children_id: nextProps.children_id
    //     })
    // },

    execute(n) {
        // Send the command to the cell
        _this = this
        axios.post("http://127.0.0.1:5000/cell",
            {
                source: this.refs[this.state.cell_id + "-source"].value,
                cell_id: this.state.cell_id,
                n_children: n
            }
        ).then(
            // Get the cell response
            axios.get("http://127.0.0.1:5000/cell?cellid=" + _this.state.cell_id)
                .then(function(result) {
                    _this.setState({
                        ..._this.state,
                        source: result.data.source.join(''),
                        stdout: result.data.outputs.stdout,
                        children_id: result.data.children_id
                    })
                })
            )
    },

    render() {
        const textareaStyle = {
            margin: 'auto',
            border: 'none',
            resize: 'none',
            width: '100%',
            padding: '5px',
            fontSize: '14px',
            whiteSpace: 'pre',
            fontFamily: '"Lucida Console", monospace',
            backgroundColor: 'white'
        };

        return (
            <div className="cell">
                <button onClick={() => this.execute(1)}>exec</button>
                <button onClick={() => this.execute(2)}>branch</button>
                <p>{this.state.cell_id}</p>
                <Textarea
                    style={textareaStyle}
                    minRows='8'
                    defaultValue={this.state.source}
                    ref={this.state.cell_id + "-source"}/>
                <code>{this.state.stdout}</code>
            </div>
        )
    }
})

var Notebook = React.createClass({

    propTypes: {
        count: function(props, propName) {
            if(typeof props[propName] !== "number") {
                return new Error("the count must be a number")
            }
        }
    },

    getInitialState() {

        var cells = []
        this.current_cell = {
                cell_id: 'cell-0',
                source: '',
                stdout: '',
                parent_id: null,
                children_id: []
            }
        cells.push(this.current_cell)

        return {
            cells: cells,
            current_cell: this.current_cell
        }
    },

    add(source, stdout) {

        _this = this
        axios.get("http://127.0.0.1:5000/cell?cellid=" + _this.current_cell.cell_id)
            .then(function(result) {
                children_id = result.data.children_id

                _this.current_cell.children_id = children_id

                var cells = [
                    ..._this.state.cells
                ]

                for(i = 0; i < children_id.length; i++) {
                    var cell_id = children_id[i]
                    var new_cell = {
                        cell_id: cell_id,
                        source: source,
                        stdout: stdout,
                        parent_id: _this.current_cell.parent_id,
                        children_id: []
                    }
                    cells.push(new_cell)
                    _this.current_cell = new_cell
                }
                _this.setState({cells})
            })
    },

    update(new_source, cell_id) {
        var cells = this.state.cells.map(
                cell => (cell.cell_id !== cell_id) ? cell : {
                    ...cell, 
                    source: new_source
                }
            )
        this.setState({cells})
    },

    eachCell(cell) {
        return (
            <Cell key={cell.cell_id}
                cell_id={cell.cell_id}
                source={cell.source}
                stdout={cell.stdout}
                parent_id={cell.parent_id}
                children_id={cell.children_id}
                onChange={this.update}>
            </Cell>
        )
    },

    render() {
        return (
            <div className="board">
                {this.state.cells.map(this.eachCell)}
                <button onClick={() => this.add('', '')}>+</button>
            </div>
        )
    }
})

ReactDOM.render(<Notebook count={10}/>, document.getElementById('react-container'))