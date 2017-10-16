import commandEngine from './commandEngine';

const terminal = (state = { history: ['there is no history'], input: '', inputDisabled: false}, action) => {  
    switch (action.type) {
        case 'INPUT_ENTERED':
            let addHistory = [action.value];
            let inputDisabled = true;
            let commandStatus = commandEngine.runCommand(action.value)
            if (!commandStatus)
            {
                if (action.value)
                {
                    addHistory.push("bad command");
                }
                
                inputDisabled = false;
            }

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
