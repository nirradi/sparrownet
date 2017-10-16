

const terminal = (state = { history: ['there is no history'], input: '', inputDisabled: false}, action) => {  
    switch (action.type) {
        case 'INPUT_ENTERED':
            let addHistory = [action.value];
            let inputDisabled = true;

            return {
                ...state,
                history: state.history.concat(addHistory),
                inputValue: '',
                inputDisabled
            }
        case 'ADD_OUTPUT':
            return {
                ...state,
                history: state.history.concat(action.value),
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
