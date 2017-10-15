import {  
  applyMiddleware,
  combineReducers,
  createStore,
} from 'redux';


import thunk from 'redux-thunk';

import terminal from '../gamestate/terminal.js';

let reducers = combineReducers({
    terminal
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