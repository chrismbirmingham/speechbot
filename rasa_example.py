import requests


def send_to_rasa(text="Hi there!"):
    headers = {
        'Content-Type': 'application/json',
    }

    data = '{ "sender": "test_user", "message": "' + text + '", "metadata": {} }'

    response = requests.post('http://localhost:5005/webhooks/myio/webhook', headers=headers, data=data)
    print(f"Bot response: \n{response.text}\n")
    try:
        text = response.json()[0]["text"]
    except IndexError:
        print("Warning: Bad index")
        text = "I didn't catch that"
    return text


if __name__ == '__main__':
    r = "Let's start a conversation with the rasa bot. What would you like to say?\n->"
    while True:
        i = input(r)
        r = send_to_rasa(i) + "\n->"
