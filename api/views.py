from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
import openai

import os ,json

secret_file = os.path.join('/home','oh','sweetbot','gpt_romance','secrets.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())
    
def get_secret(setting,secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = f"{setting}"
        raise ImproperlyConfigured(error_msg)

openai.api_key = get_secret("SECRET_KEY")


def generate_text(request):
    prompt = request.POST.get('prompt')
    model = "gpt-3.5-turbo"
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        max_tokens=50
    )
    return HttpResponse(response.choices[0].text)



# this is the home view for handling home page logic
def home(request):
    try:
        # if the session does not have a messages key, create one
        if 'messages' not in request.session:
            request.session['messages'] = [
                {"role": "system", "content": "지금부터 너는 내 애인이야.."},
            ]
        if request.method == 'POST':
            # get the prompt from the form
            prompt = request.POST.get('prompt')
            # get the temperature from the form
            temperature = float(request.POST.get('temperature', 0.1))
            # append the prompt to the messages list
            request.session['messages'].append({"role": "user", "content": prompt})
            # set the session as modified
            request.session.modified = True
            # call the openai API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=request.session['messages'],
                temperature=temperature,
                max_tokens=1000,
            )
            # format the response
            formatted_response = response['choices'][0]['message']['content']
            # append the response to the messages list
            request.session['messages'].append({"role": "chat", "content": formatted_response})
            request.session.modified = True
            # redirect to the home page
            context = {
                'messages': request.session['messages'],
                'prompt': '',
                'temperature': temperature,
            }
            return render(request, 'home.html', context)
        else:
            # if the request is not a POST request, render the home page
            context = {
                'messages': request.session['messages'],
                'prompt': '',
                'temperature': 0.1,
            }
            return render(request, 'home.html', context)
    except Exception as e:
        print(e)
        # if there is an error, redirect to the error handler
        return redirect('error_handler')

def new_chat(request):
    # clear the messages list
    request.session.pop('messages', None)
    return redirect('home')

# this is the view for handling errors
def error_handler(request):
    return render(request, '404.html')