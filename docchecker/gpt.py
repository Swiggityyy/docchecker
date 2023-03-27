# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import keys

openai.organization = keys.organizationid
openai.api_key = keys.apikey
openai.Model.list()

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": eprompt}
    ]
)

print(completion.choices[0].message.content)

