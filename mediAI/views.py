from django.http import JsonResponse
from django.shortcuts import render
import time

from .chatgpt_module import ChatGPT 

chat_assistant = ChatGPT()

# Create your views here.
def chatgpt(request):

    return render(request, 'chatgpt.html')

def ajax_submit(request):
    msger_input = request.POST['msger_input']
    role = "provider"
    answer, sources = chat_assistant.get_response(msger_input, role)

    response = {
        "answer": answer,
    }

    # for testing
    # response = {
    #     "answer": "This is a test response",
    # }
    return JsonResponse(response)