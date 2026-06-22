#This is where the ai will create messages

import os
from groq import Groq
from dotenv import load_dotenv

#Load the .env file
load_dotenv()

client = Groq(api_key = os.getenv('Groq_API_KEY'))



def explain_movement(symbol, old_price, new_price, difference):

    #Variable to send to the ai bot
    prompt = f"Here is the symbol of the stock {symbol} Here is the old and then new price  {old_price} , {new_price},  Here is the diffence in % between them {difference}, now I need you to write a message to the user explaining if it was a rise or fall in price and why but if there is no clear why then put nothing. also make it short not long. Do not use the symbol but the name that is tied to it so the real company name"

    #create the model and call the prompt
    response = client.chat.completions.create(model = "llama-3.3-70b-versatile", messages = [{"role" : "user", "content": prompt}])

    return response.choices[0].message.content
