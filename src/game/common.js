import pluralize from 'pluralize';

export function mailbox(mails) {
    return {
        'func': function (command) {
            let unreadMailCount = mails.unread.length;
            
            let args = command.split(' ');
            args.shift();
            if (args.length === 0)
            {
                this.sendToOutput('You have ' + unreadMailCount + ' unread ' + pluralize('e-mail', unreadMailCount) + " in your mailbox");
                this.pushShell({
                    'next': {
                        'func': function() {
                            if (mails.unread.length === 0)
                            {
                                this.sendToOutput('there are no more unread e-mails');    
                            }
                            else {
                                let delimiter="------------------------\r\n";
                                let currentMail = mails.unread.shift();
                                mails.read.push(currentMail);
                                this.sendToOutput(delimiter + "from: " + currentMail.from +
                                    "\r\n" + delimiter +"\r\nsent at: " + currentMail.sent + 
                                    "\r\n" + delimiter +"\r\nbody: " + currentMail.body );    
                            }
                        },
                        'description': 'read next unread mail'
                    },
                    'quit': {
                        'func': function() {
                            this.popShell();
                        },
                        'description': 'quit the mailbox'
                    },
                }, 'mailbox > ')
            }
        },
        'description': 'opens the mailbox'
    }
}