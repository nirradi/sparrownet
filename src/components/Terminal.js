import React, { Component } from 'react';
import TerminalOutput from './TerminalOutput';
import TerminalInput from './TerminalInput';

class Terminal extends Component {
    render() {
        return (
            <div className="App">
                    <h1> Terminal </h1>
                    <TerminalOutput history={this.props.terminal.history}/>
                    <TerminalInput disabled = {this.props.terminal.inputDisabled} inputValue={this.props.terminal.inputValue} onEnter= {this.props.inputEntered} />
                </div>
        );
    }
}

export default Terminal;
