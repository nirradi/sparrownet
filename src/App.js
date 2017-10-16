import React, { Component } from 'react';
import Terminal from './containers/TerminalContainer';
import store from './store/store.js';
import { Provider } from 'react-redux';  

import './style/css/main.css';

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
