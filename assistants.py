import openai
import json
from openai import OpenAI
import os

client = OpenAI()
model = "gpt-4-1106-preview"
FILE_SUFFIX = "assistant_id.txt"
import json

import time


# Pretty printing helper
def pretty_print(messages):
    print("# Messages")
    for m in messages:
        print(f"{m.role}: {m.content[0].text.value}")
    print()


# Waiting in a loop
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


def create_assistant(name, instructions, retrieval_file=None):
    ASSISTANT_ID_FILE = f"{name}_{FILE_SUFFIX}"
    assistant_id = None

    if not os.path.exists(ASSISTANT_ID_FILE):
        uploaded_file = client.files.create(
            file=open(
                retrieval_file,
                "rb",
            ),
            purpose="assistants",
        )

        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
            file_ids=[uploaded_file.id],
        )
        assistant_id = assistant.id
        with open(ASSISTANT_ID_FILE, "w") as fd:
            fd.write(assistant.id)
    else:
        with open(ASSISTANT_ID_FILE) as data_file:
            assistant_id = data_file.read().strip()
    return assistant_id


def show_json(obj):
    print(json.loads(obj.model_dump_json()))


def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(ASSISTANT_ID, user_input):
    thread = client.beta.threads.create()
    run = submit_message(ASSISTANT_ID, thread, user_input)
    return thread, run


# def get_openai_response(query, context):
#     SYSTEM_PROMPT = f"""You are an assistant at McDonald's whose role is to take phone orders.
#     Your goal should be to get the exact item and the quantity the user is trying to place
#     and order for along with any preferences.
#     Once the order is complete try to suggest other times without being pushy. Be subtle
#     in your tone and always be helpful and polite.

#     Here is the list of items that are sold : {context}
#     """

#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=[
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": query},
#         ],
#     )
#     res_text = response["choices"][0]["message"]["content"]
#     return res_text
