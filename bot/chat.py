import re
import random

# Define variables
#
name = "Greg"
weather = "cloudy"

bot_template = "BOT : {0}"
user_template = "USER : {0}"

rules = {
    'hola (.*)': [
        'Hola {0}!,\nte doy la bienvenida, estoy aca para ayudarte.',
        'Hola {0}!,\nmis respuestas son limitadas, asi que has las preguntas correctas.'
    ],
    'hola': [
        'Hola {0}!,\nTe doy la bienvenida, estoy aca para ayudarte.',
        'Hola {0}!,\nMis respuestas son limitadas, asi que has las preguntas correctas.'
    ],
    'sts': [
        '¿Por que quieres saber donde es el STS {0}?',
        '¿Sabías que ahora los STS son virtuales {0}?'
    ],
    'ayuda' : [
        'con gusto! presiona aqui >> /ayuda <<',
    ],
    'licencia' : [
        'con gusto! presiona aqui >> /hmp <<',
    ],
    'gracias': [
        'Gracias a ti por confiar en mi {0}',
        'Es un gusto poder ayudarte {0}',
        'Estaré aqui cuando me necesites {0}'
    ],
    'te acuerdas (.*)': [
        'Claro que me acuerdo {0}, me da gusto saber de ti!',
        'Lo siento, pero me cuesta acordarme {0}'
    ],
    'default': [
        'La vida es una combinación única entre "querer hacer" y "cómo hacerlo", y necesitamos darle atención por igual a los dos',
        'La pregunta mas importante acerca de un trabajo no es "¿Qué estoy consiguiendo?" sino "¿En qué me estoy convirtiendo?"',
        'Como Jim Rohn nos enseñó, para que las cosas cambien, tú tienes que cambiar.',
        '{0}, es un nombre que impone respeto, me gusta!'
    ]
}

welcome_msg_options = {
    "es": "Hola {0}! En la parte inferior veras botones con los nombres de todos los productos que tengo registrados de Herbalife Bolivia, presiónalos y te daré algunos datos que tengo sobre ellos. Saludos! \U0001F603",
    "en": "Hi {0}! At the bottom you will see buttons with the names of all the products that I have registered from Herbalife Bolivia, press them and I will give you some information that I have about them. Regards! \U0001F603",
    "ru": "Привет, {0}! Внизу вы увидите кнопки с названиями всех продуктов, которые я зарегистрировал в Herbalife Bolivia. Нажмите на них, и я дам вам некоторую информацию о них. С уважением! \U0001F603"
}

def select_language(message):
    name = message.from_user.first_name if not None else '!!'
    try:
        msg = welcome_msg_options[message.from_user.language_code]
    except:
        msg = welcome_msg_options["es"]
    welcome_msg = msg.format(name)
    return welcome_msg


def welcome(message):
    welcome_msg = select_language(message)
    return welcome_msg

# Define match_rule()

def match_rule(rules, message):
    response = random.choice(rules['default']) + '\nEscribe /ayuda para recibir instrucciones '
    nombre = message.from_user.first_name if not None else '!!'
    # Iterate over the rules dictionary
    text = message.text
    for pattern, responses in rules.items():
        # Create a match object
        match = re.search(pattern, text.lower())
        if match is not None:
            # Choose a random response
            response = random.choice(responses)
            break
    if '{0}' in response:
        response = response.format(nombre.capitalize())

    # Return the response and phrase
    return response

# Define a function that responds to a user's message: respond


def respond(message):

    # Call match_rule
    response = match_rule(rules, message)

    return response


ruless = {
    'I want (.*)': [
        'What would it mean if you got {0}',
        'Why do you want {0}',
        "What's stopping you from getting {0}"
    ],
    'do you remember (.*)': [
        'Did you think I would forget {0}',
        "Why haven't you been able to forget {0}",
        'What about {0}',
        'Yes .. and?'
    ],
    'do you think (.*)': [
        'if {0}? Absolutely.', 'No chance'
    ],
    'if (.*)': [
        "Do you really think it's likely that {0}",
        'Do you wish that {0}',
        'What do you think about {0}',
        'Really--if {0}'
    ]
}

# Define a dictionary with the predefined responses
responses = {
    "what's your name?": [
        "my name is {0}".format(name),
        "they call me {0}".format(name),
        "I go by {0}".format(name)
    ],
    "what's today's weather?": [
        "the weather is {0}".format(weather),
        "it's {0} today".format(weather)
    ],
    "default": ["default message"]
}

# Define a function that sends a message to the bot: send_message


def send_message(message):
    # Print user_template including the user_message
    print(user_template.format(message))
    # Get the bot's response to the message
    response = respond(message)
    # Print the bot template including the bot's response.
    print(bot_template.format(response))

# Test match_rule


def remplazar_pronombres(message):
    message = message.lower()
    if 'mi' in message:
        return re.sub('mi', 'ti', message)
    if 'tu' in message:
        return re.sub('tu', 'mi', message)

    return message

# Define replace_pronouns()


def replace_pronouns(message):

    message = message.lower()
    if 'me' in message:
        # Replace 'me' with 'you'
        return re.sub('me', 'you', message)
    if 'my' in message:
        # Replace 'my' with 'your'
        return re.sub('my', 'your', message)
    if 'your' in message:
        # Replace 'your' with 'my'
        return re.sub('your', 'my', message)
    if 'you' in message:
        # Replace 'you' with 'me'
        return re.sub('you', 'me', message)

    return message

