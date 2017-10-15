import React from 'react';

class TerminalInput extends React.Component {
    
    constructor(props) {
        super();
        this.state = {
            value: props.inputValue
        };
    }
    
    keyPress(e){
        if(e.keyCode === 13){
            this.props.onEnter(e.target.value)
        }
    }
    
    onChange(e) {
        this.setState({value: e.target.value});
    }
    
    componentWillReceiveProps(nextProps) {
        this.setState({value: nextProps.inputValue});
    }
    
    render() {
        return (
            <div>
                <input disabled={this.props.disabled} value={this.state.value} onKeyDown={this.keyPress.bind(this)} onChange={this.onChange.bind(this)}/>
            </div>
        );
    }
}

TerminalInput.defaultProps = {
    inputValue:'', 
    inputDisabled: false
}

export default TerminalInput;