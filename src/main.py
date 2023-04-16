import openai
import subprocess

with open('prompt.txt', 'r') as file:
    prompt = file.read()

with open('system.txt', 'r') as file:
    system = file.read()

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ]
)

command = (response['choices'][0]['message']['content'])
command = command.replace('```', '').strip()

print('underling> ' + command)
answer = input("Run above command? (y/n): ")
if answer.lower() == 'y':
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)
    print(result.stderr)
