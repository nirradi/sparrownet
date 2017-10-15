import store from '../store/store' ;

import {  
  sendToOutput,
} from '../store/actions';


export default {
    runCommand: function(command) {
        if (store.getState().gameState.availableCommands.hasOwnProperty(command))
        {
            setTimeout(store.getState().gameState.availableCommands[command].bind(this), 1);
            return true;
            
        }
        else
            return false;
    },
    
    sendToOutput: function(value) {
        store.dispatch(sendToOutput(value));
    }
}