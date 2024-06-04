import requests

def call_flask_api(user_input):
    url = "http://-:5000/process_text"
    data = {"input": user_input}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        prompt = result['context']
        title = result['title']
        print("context:", prompt)
        print("Title:", title)
    else:
        print("Error:", response.text)

if __name__ == "__main__":
    user_input = input("Enter your question: ")
    call_flask_api(user_input)
