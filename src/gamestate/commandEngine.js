import store from '../store/store' ;

import {  
  sendToOutput,
  returnInput
} from '../store/actions';


export default {
    runCommand: function(command) {
        if (store.getState().gameState.availableCommands.hasOwnProperty(command))
        {
            let self = this;
            setTimeout(function() {
                (store.getState().gameState.availableCommands[command].bind(self))();
                store.dispatch(returnInput());
            }, 1);
            return true;
            
        }
        else
            return false;
    },
    
    sendToOutput: function(value) {
        store.dispatch(sendToOutput(value));
    }
}