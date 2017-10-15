import Terminal from '../components/Terminal';
import { connect } from 'react-redux';
import {  
  inputEntered,
} from '../store/actions';

const mapStateToProps = (state, ownProps) => ({
    terminal: state.terminal 
});

const mapDispatchToProps = {
    inputEntered
}

export default connect(mapStateToProps, mapDispatchToProps)(Terminal)