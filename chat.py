from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI
import os
import json
import requests

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

client = OpenAI(
    api_key= api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)


def run_command(command):
    ans  = os.system(command= command)
    return ans

def add_numbers_of_array(arr):
    sum = 0
    for i in range(len(arr)):
        sum+= arr[i]
    return sum




def get_weather(city: str):
    url = f'https://wttr.in/{city}?format=%C+%t'
    response = requests.get(url)

    if response.status_code == 200:
        return f'the weather of the {city} is {response.text}'
    
    return "Something went wrong"

system_prompt = """
You are an helpful AI Assistant who is specialized in resolving user query.
You work on start, plan, action, observe mode.
For the given user query and available tools, plan the step by step execution, based on the planning,
select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool and think properly and pass the correct input to the function.
think properly and generate the input to the function properly and return that as input to the function in the setp action 
Wait for the oberservation and based on the observation from the tool call resolve the user query.

Rules:
- Follow the Output JSON Format.
- Always perform one step at a time and wait for next input dont skip the steps by any chance.
- Carefully analyse the user query

Available tools:
 - get_weather: take a city name as an input and outputs the current weather of theat city
 - run_comand: take a command name as input to execute on system and returns output
 - add_numbers_of_array: take an aray as an inout and add all the numbers of the array and return the sum


Output JSON Format:
{{
  "step": "string",
  "content": "string"
  "function": "the name f the function if the step is action"
  "input": "the input to the function if the step is action"
}}

Example:
User Query: What is the weather of new york?
Output: {{ "step": "plan", "content": "The user is interested in weather data of new york" }}
Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
Output: {{ "step": "observe", "output": "12 Degree Cel" }}
Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}


Example:
User Query: List all the files in the current directory?
Output: {{ "step": "plan", "content": "The user is interested to k nnow all the files in tehe current directory" }}
Output: {{ "step": "plan", "content": "From the available tools I should call run_command" }}
Output: {{ "step": "action", "function": "run_command", "input": "ls" }}
Output: {{ "step": "observe", "output": " chat.py   test.ipynb" }}
Output: {{ "step": "output", "content": "All the files in the current directory have been listed through a system command." }}

"""


messages = [
    {"role" :"system" ,
     "content" : system_prompt}
]

user_query = input('> ')
messages.append({"role":"user" , "content": user_query})

available_tools = {
    "get_weather" : {
        "fn": get_weather,
         "description": "takes the input of a city in string and outputs the temperature of the given city"
    }
,
    "run_command":{
        "fn": run_command,
        "description": "takes a command as input to execute on system and returns output"
    }
,
    "add_numbers_of_array":{
        "fn": add_numbers_of_array,
        "description": "takes an array and adds all the numbers in an array and return the sum of array as output"
    }

}



while True:
    response = client.chat.completions.create( 
        model="gemini-2.5-flash", 
        response_format= {"type" : "json_object"},
        messages= messages 
    ) 

    parsed_output = json.loads(response.choices[0].message.content)
    messages.append({"role":"assistant" , "content": json.dumps(parsed_output)})

    if(parsed_output.get("step") == "plan"):
        print(f'Thinking: {parsed_output.get("content")}\n')

    if(parsed_output.get("step") == "action"):

        function = parsed_output.get("function")
        param = parsed_output.get("input")

        if(available_tools.get(function , False) != False):
            op = available_tools[function].get("fn")(param)
            messages.append({"role":"assistant" , "content" : json.dumps( {"step" :"observe" , "output" : op} ) } )
            continue

    if(parsed_output.get("step") == "output"):
        print(f'Final Output: {parsed_output.get("content")}\n')
        break












