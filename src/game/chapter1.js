import { mailbox } from './common';


var chapter1 = {
    rootCommands: {
    },
    initialOutput: "Welcome to sparrownet terminal (v2.14.1)\nImportant*: Your system is not up-to-date. Please speak with your system adminstrator.",
    mails: {
        unread: [
            {
                from: 'Elda Vice',
                to: 'Taylor Fen',
                sent: '3 days ago',
                body: 'Hi Taylor \n How are you? \n I\'ve been worried lately, you haven\'t sent in your daily report for 3 days now, are you ok?' 
            },
            {
                from: 'Elda Vice',
                to: 'Taylor Fen',
                sent: 'Yesterday',
                body: 'Taylor - please send me a mail once you get this, I need to tell you something important'
            }
        ],
        read: [
        ]
    }
}

chapter1.rootCommands.mailbox = mailbox(chapter1.mails);

export default chapter1;