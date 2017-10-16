import Terminal from '../components/Terminal';
import { connect } from 'react-redux';
import commandEngine from '../gamestate/commandEngine';
const mapStateToProps = (state, ownProps) => ({
    terminal: state.gameState
});


const mapDispatchToProps = (dispatch) => {
    return {
        inputEntered: commandEngine.runCommand
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(Terminal)