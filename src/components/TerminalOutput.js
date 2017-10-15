import React from 'react';

class TerminalOutput extends React.Component {
    
    render() {
        let displayItems = [];
        this.props.history.forEach(function(historyItem) {
            displayItems.push(<div>{historyItem}</div>)
        })
        return (
            <div>
                {displayItems}
            </div>
        );
    }
}

TerminalOutput.defaultProps = {
    history: ['the history is empty']
};
    

export default TerminalOutput;