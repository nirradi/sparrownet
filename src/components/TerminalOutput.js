import React from 'react';


class TerminalOutput extends React.Component {
    
    render() {
        let displayItems = [];
        this.props.value.forEach(function(outputItem) {
            displayItems.push(<div>{outputItem}</div>)
        })
        return (
            <div className='terminal-output'>
                {displayItems}
            </div>
        );
    }
}

TerminalOutput.defaultProps = {
    value: ['-------------']
};
    

export default TerminalOutput;