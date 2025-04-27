import openai
import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)

# Replace with your OpenAI API key
openai.api_key = "sk-proj"  # <-- Replace with your OpenAI key

@csrf_exempt
def chat_view(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    if 'conversation' not in request.session:
        request.session['conversation'] = []
        request.session['user_name'] = None

    if request.method == "POST":
        user_message = request.POST.get('message', '').strip()

        if "my name is" in user_message.lower():
            name = user_message.split("my name is")[-1].strip().capitalize()
            request.session['user_name'] = name
            bot_message = f"Nice to meet you, {name}! How are you feeling today?"
        else:
            name = request.session.get('user_name')

            if name and "what's my name" in user_message.lower():
                bot_message = f"Your name is {name}!"
            else:
                conversation_history = request.session['conversation']
                conversation_history.append({"role": "user", "content": user_message})

                if "bye" in user_message.lower():
                    full_conversation = [
                        {"role": "system", "content": "You are a caring, mature, and empathetic psychiatrist."}
                    ] + conversation_history

                    try:
                        # Debugging OpenAI API request
                        logger.debug("Sending request to OpenAI API...")

                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=full_conversation
                        )

                        # Log the response to check if OpenAI is sending back any data
                        logger.debug(f"OpenAI response: {response}")

                        bot_message = response['choices'][0]['message']['content'].strip()

                        # Performing mental health analysis if conversation ends with "bye"
                        analysis_prompt = "Based on the following conversation, highlight key points about their mental health and give advice:\n"
                        analysis_prompt += "\n".join([f"{msg['role']}: {msg['content']}" for msg in full_conversation])

                        analysis_response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": "You are a mental health analysis assistant."},
                                      {"role": "user", "content": analysis_prompt}]
                        )

                        mental_health_analysis = analysis_response['choices'][0]['message']['content'].strip()
                        bot_message += f"\n\n*Mental Health Analysis:* {mental_health_analysis}"

                        request.session['conversation'] = []
                    except openai.error.OpenAIError as e:
                        logger.error(f"OpenAI API error: {str(e)}")
                        bot_message = f"Error during analysis: {str(e)}"
                    except Exception as e:
                        logger.error(f"General error during OpenAI API call: {str(e)}")
                        bot_message = f"General Error: {str(e)}"
                else:
                    try:
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "system", "content": "You are a caring, mature, and empathetic psychiatrist."},
                                      *conversation_history]
                        )
                        bot_message = response['choices'][0]['message']['content'].strip()
                    except openai.error.OpenAIError as e:
                        logger.error(f"OpenAI API error: {str(e)}")
                        bot_message = f"Error: {str(e)}"
                    except Exception as e:
                        logger.error(f"General error during OpenAI API call: {str(e)}")
                        bot_message = f"Error: {str(e)}"

                conversation_history.append({"role": "assistant", "content": bot_message})
                request.session['conversation'] = conversation_history

        return JsonResponse({"response": bot_message})

    return render(request, 'chat/chat.html')


    def signup_view(request):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        else:
                form = UserCreationForm()
    return render(request, 'chat/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat')  # Redirect to chat after successful login
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')
