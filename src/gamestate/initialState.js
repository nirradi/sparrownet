import commandEngine from './commandEngine';

export default {
    availableCommands: {
        'help':  function () {
            commandEngine.sendToOutput('hahahaha');
        }
    }
}