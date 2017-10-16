

const terminal = (state = { prompt: '> ', shellStack: [], output: [], input: '', inputDisabled: false, availableCommands: []}, action) => {  
    switch (action.type) {
        case 'INPUT_ENTERED':
            let add = [state.prompt + action.value];
            let inputDisabled = true;

            return {
                ...state,
                output: state.output.concat(add),
                inputDisabled
            }
        case 'ADD_OUTPUT':
            return {
                ...state,
                output: state.output.concat(action.value),
                inputDisabled: !action.returnInput
            }
        case 'RETURN_INPUT':
            return{
                ...state,
                inputDisabled: false
            }
        case 'PUSH_SHELL': 
            let newShellStack = state.shellStack.concat({
                commands: state.availableCommands,
                prompt: state.prompt
            });
            return {
                ...state,
                shellStack: newShellStack,
                availableCommands: action.commands,
                prompt: action.prompt, 
                inputDisabled: false
            }
        case 'POP_SHELL': 
            
            return {
                ...state,
                availableCommands: state.shellStack[state.shellStack.length - 1].commands,
                prompt: state.shellStack[state.shellStack.length - 1].prompt,
                shellStack: state.shellStack.slice(0, -1),
                inputDisabled: false
            }

        default:
            return state;
    }
};

export default terminal;
