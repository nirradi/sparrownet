def get_user_input():
    # read a line from command prompt
    return input(">> ")


def interpret_input(input: str):
    
def loop():    
    state = initialize_game_state()
    while True:
        input = get_user_input()
        intent, ok = interpret_input(input)
        if ok:
            apply_intent_to_state(state, intent)
        else:
            response = generate_bad_response(state, intent)
        
        response = generate_response(state, intent)

        display_response(response)


