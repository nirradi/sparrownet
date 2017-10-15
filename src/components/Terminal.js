import React, { Component } from 'react';
import TerminalOutput from './TerminalOutput';
import TerminalInput from './TerminalInput';

class Terminal extends Component {
    render() {
        return (
            <div className="App">
                    <h1> Terminal </h1>
                    <TerminalOutput history={this.props.terminal.history}/>
                    <TerminalInput onEnter= {this.props.inputEntered} />
                </div>
        );
    }
}

export default Terminal;
