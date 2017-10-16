export const inputEntered = value => ({  
  type: 'INPUT_ENTERED',
  value,
});

export const sendToOutput = value => ({  
  type: 'ADD_OUTPUT',
  value,
});

export const returnInput = () => ({  
  type: 'RETURN_INPUT'
});