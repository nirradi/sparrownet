import React, { Component } from 'react';
import TerminalOutput from './TerminalOutput';
import TerminalInput from './TerminalInput';

class Terminal extends Component {
    
    render() {
        return (
            <div className="terminal">
                    <TerminalOutput value={this.props.terminal.output}/>
                    <TerminalInput 
                        disabled={this.props.terminal.inputDisabled} 
                        inputValue={this.props.terminal.inputValue} 
                        onEnter={this.props.inputEntered} 
                        availableCommands={Object.keys(this.props.gameState.availableCommands)}
                    />
                </div>
        );
    }
}

export default Terminal;
