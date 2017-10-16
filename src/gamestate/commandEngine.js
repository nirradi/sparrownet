import store from '../store/store' ;

import {  
    inputEntered,
    sendToOutput,
    pushShell,
    popShell,
    returnInput
} from './terminalActions';


var commandEngine = {
    
    start: function(initialState) {
        store.dispatch(pushShell(initialState.rootCommands, '> '))
        store.dispatch(sendToOutput(initialState.initialOutput));
    },
    
    sendToOutput: function(value, disable=true) {
        store.dispatch(sendToOutput(value));
    },
    
    runCommand: function(fullCommand) {
        let command = fullCommand.split(' ')[0];
        store.dispatch(inputEntered(fullCommand));
        let availableCommands = store.getState().gameState.availableCommands;
        if (command === '') {
            store.dispatch(returnInput());
        }
        else if (command === 'help')
        {
            commandEngine.showHelp(availableCommands)
        }
        else if (availableCommands.hasOwnProperty(command))
        {
            setTimeout((availableCommands[command].func.bind(commandEngine))(fullCommand), 1);
        }
        else {
            commandEngine.sendToOutput("bad command");    
        }
    },
   
    showHelp: function(availableCommands) {
        commandEngine.sendToOutput("action       | Description\r\n--------------------");
        for (var availableCommand in availableCommands) {
            if (availableCommands.hasOwnProperty(availableCommand)) {
                commandEngine.sendToOutput((availableCommand + "                  ").slice(0, 12) + "| " + availableCommands[availableCommand].description);        
            }
        };
    },
    
    pushShell: function(commands, prompt) {
        store.dispatch(pushShell(commands, prompt));
    },
    
    popShell: function() {
        store.dispatch(popShell());
    }
}

export default commandEngine;