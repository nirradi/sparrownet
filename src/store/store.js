import {  
  applyMiddleware,
  combineReducers,
  createStore,
} from 'redux';


import thunk from 'redux-thunk';

import terminal from '../gamestate/terminal.js';
import gameState from '../gamestate/gameState.js';

let reducers = combineReducers({
    terminal,
    gameState
});

export function configureStore(initialState = {}) {  
  const store = createStore(
    reducers,
    initialState,
    applyMiddleware(thunk)
  )
  return store;
};

const store = configureStore(); 

export default store;