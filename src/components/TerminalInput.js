import React from 'react';

class TerminalInput extends React.Component {
    
    keyPress(e){
      if(e.keyCode === 13){
         this.props.onEnter(e.target.value)
      }
   }
    
    render() {
        return (
            <div>
                <input onKeyDown={this.keyPress.bind(this)} onChange={this.props.onChange}/>
            </div>
        );
    }
}


export default TerminalInput;