import React, { Component } from 'react';
import Terminal from './containers/TerminalContainer';
import store from './store/store.js';
import { Provider } from 'react-redux';  
import commandEngine from './gamestate/commandEngine';
import initialState from './game/chapter1';
import './style/css/main.css';

commandEngine.start(initialState);

class App extends Component {
    render() {
        return (
            <Provider store = {store}>
                <Terminal/>
            </Provider>
        );
    }
}

export default App;
