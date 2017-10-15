import React, { Component } from 'react';
import Terminal from './containers/TerminalContainer';
import store from './store/store.js';
import { Provider } from 'react-redux';  

import './App.css';

class App extends Component {
    render() {
        return (
            <Provider store = {store}>
                <div className="App">
                    <Terminal/>
                </div>
            </Provider>
        );
    }
}

export default App;
