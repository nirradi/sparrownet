import store from '../store/store' ;

import {  
    inputEntered,
    sendToOutput
} from './actions';


export default {
    runCommand: function(command) {
        let self = this;
        store.dispatch(inputEntered(command));
        
        if (store.getState().gameState.availableCommands.hasOwnProperty(command))
        {
            
            setTimeout(store.getState().gameState.availableCommands[command].bind(self), 1);
        }
        else {
            store.dispatch(sendToOutput("bad command"));    
        }
    },
    
    sendToOutput: function(value) {
        store.dispatch(sendToOutput(value));
    }
}