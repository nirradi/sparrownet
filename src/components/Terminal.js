import React, { Component } from 'react';
import TerminalOutput from './TerminalOutput';
import TerminalInput from './TerminalInput';

class Terminal extends Component {
    
    render() {
        return (
            <div className="terminal">
                    <TerminalOutput value={this.props.terminal.output}/>
                    <TerminalInput 
                        prompt={this.props.terminal.prompt}
                        disabled={this.props.terminal.inputDisabled} 
                        inputValue={this.props.terminal.inputValue} 
                        onEnter={this.props.inputEntered} 
                        availableCommands={Object.keys(this.props.terminal.availableCommands)}
                    />
                </div>
        );
    }
}

export default Terminal;
