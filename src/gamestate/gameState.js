import initialState from './initialState';

const gameState = (state = initialState, action) => {  
    switch (action.type) {
        default:
            return state;
    }
};

export default gameState;
