from random import choice, randint

def get_response(user_input) -> str:
    lowered: str = user_input.lower()
    
    if lowered == '':
        return 'I am a bot that can respond to your messages. Try asking me a question!'
    elif 'Account info' in lowered:
        return 
    elif 'how are you' in lowered:
        return 'I am doing well, how about you?'
    elif 'good' in lowered:
        return 'That is nice to hear'
    elif 'bad' in lowered:
        return 'I am sorry to hear that'
    elif 'roll dice' in lowered:
        return str(randint(1, 6))
    else: 
        return choice(['I do not understand',
                        'I am sorry, I do not understand',
                        'What are you talking about'])