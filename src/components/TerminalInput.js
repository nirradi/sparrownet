import React from 'react';
import keycode from 'keycode'
class TerminalInput extends React.Component {
    
    constructor(props) {
        super();
        this.state = {
            value: props.inputValue,
            commandHistory: props.commandHistory,
            commandHistoryPosition: 0,
        };
    }
    
    keyPress(e) {
        if (e.keyCode === keycode('Enter'))
        {
            this.props.onEnter(e.target.value); 
            this.setState({ 
                commandHistory: this.state.commandHistory.concat(e.target.value),
                commandHistoryPosition: this.state.commandHistory.length + 1,
                value: '',
            });
        }
        
        if (e.keyCode === keycode('up') && this.state.commandHistoryPosition > 0)
        {
            this.navigateHistory(-1);
        }
        
        if (e.keyCode === keycode('down') && this.state.commandHistoryPosition < this.state.commandHistory.length)
        {
            this.navigateHistory(+1);
        }
        
        if (e.keyCode === keycode('tab'))
        {
            e.preventDefault();
            let completeCommand = '';
            let currentCommand = this.state.value;
            this.props.availableCommands.forEach(function(command) {
                if (command.indexOf(currentCommand) === 0)
                    completeCommand = command;
            });
            
            if (completeCommand)
                this.setState({value: completeCommand});
        }
        
    }
    
    navigateHistory(incr) {
        let newPosition = this.state.commandHistoryPosition + incr;
        let newValue = newPosition < this.state.commandHistory.length ? this.state.commandHistory[newPosition] : '';
        this.setState({
            value: newValue,
            commandHistoryPosition: newPosition
        });
    }
    
    onChange(e) {
        this.setState({value: e.target.value});
    }

    render() {
        return (
            <div className='terminal-input'>
                {this.props.prompt}<input ref={input => input && input.focus()} disabled={this.props.disabled} value={this.state.value} onKeyDown={this.keyPress.bind(this)} onChange={this.onChange.bind(this)}/>
            </div>
        );
    }
}

TerminalInput.defaultProps = {
    inputValue:'', 
    inputDisabled: false, 
    availableCommands: [],
    commandHistory: [],
    prompt: '>'
}

export default TerminalInput;