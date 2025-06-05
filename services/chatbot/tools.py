import os
from pandasai.llm import OpenAI
from pandasai import SmartDataframe
import pandas as pd

openai_llm = OpenAI(
    api_token=os.environ.get("OPENAI_API_KEY"),
)

def ask_database(question):
    df = pd.read_csv("data_source.csv")
    sdf = SmartDataframe(df, config={"llm": openai_llm, "use_duckdb":True})
    result = sdf.chat(str(question))
    print(question)
    print(result)
    return result

# Define the function declaration for the model
ask_database_function = {
     "type": "function",
     "name": "ask_database",
     "description": "if someone is asking for a question or ask to make a plot related to a data in database, use this function, its already have database access and youre allowed to access it",
     "parameters": {
         "type": "object",
         "properties": {
             "question": {
                 "type": "string",
                 "description": "A question that pandasai can understand",
             },
         },
         "required": ["question"],
     },
}

# Configure the client and tools
tools = [ask_database_function]

