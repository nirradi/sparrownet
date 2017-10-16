export const inputEntered = value => ({  
  type: 'INPUT_ENTERED',
  value,
});

export const sendToOutput = (value, returnInput) => ({  
  type: 'ADD_OUTPUT',
  value,
  returnInput: returnInput === undefined ? true : false
});

export const returnInput = () => ({  
  type: 'RETURN_INPUT'
});

export const pushShell = (commands, prompt) => ({  
  type: 'PUSH_SHELL',
  commands,
  prompt
});

export const popShell = () => ({  
  type: 'POP_SHELL',
});