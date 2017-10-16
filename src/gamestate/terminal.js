

const terminal = (state = { output: ['there is no output'], input: '', inputDisabled: false}, action) => {  
    switch (action.type) {
        case 'INPUT_ENTERED':
            let add = ['> ' + action.value];
            let inputDisabled = true;

            return {
                ...state,
                output: state.output.concat(add),
                inputValue: '',
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

        default:
            return state;
    }
};

export default terminal;
