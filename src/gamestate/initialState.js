import commandEngine from './commandEngine';

export default {
    availableCommands: {
        'help': {
            'func': function () {
            commandEngine.sendToOutput('hahahaha');
            },
            'description': 'this is the help command'
        }
    }
}