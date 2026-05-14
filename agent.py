import json
from openai import OpenAI
import time
from dta import prompt


def typewriter(text, delay=0.02):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # new line at end

# 🔑 OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-api-key-here"  # Replace with your actual API key
)

print("Quranic Guidance AI Agent (WITH MEMORY)")
print("----------------------------------------")

# Load dataset
with open("e:/web/hidaya ai agent/dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

MODEL = "meta-llama/llama-3-8b-instruct"

# 🧠 MEMORY STORE (session-only memory)
chat_history = [
    {
        "role": "system",
        "content":prompt
    }
]


def ask_ai(user_input):
    try:
        # Add user message to memory
        chat_history.append({
            "role": "user",
            "content": user_input
        })

        response = client.chat.completions.create(
            model=MODEL,
            messages=chat_history
        )

        answer = response.choices[0].message.content

        # Add AI response to memory
        chat_history.append({
            "role": "assistant",
            "content": answer
        })

        return answer

    except Exception as e:
        return f"AI Error: {e}"


while True:
    user_input = input("\nAsk your question (type 'exit' to quit):\n> ").lower().strip()

    if user_input == "exit":
        print("Goodbye! May Allah guide you always.")
        break

    # 🔹 Dataset check
    found = False
    for key in data:
        if key.lower() in user_input:
            verse = data[key]

            result = (
                "\n📖 Quranic Guidance (Dataset):\n"
                f"{verse['ayah']}\n"
                f"({verse['reference']})\n"
                f"\n💡 Message: {verse['message']}"
            )

            print(result)

            # also store in memory
            chat_history.append({
                "role": "assistant",
                "content": result
            })

            found = True
            break

    # 🔹 AI fallback with memory
    if not found:
        print("\n🧠 AI Thinking...\n")
        result = ask_ai(user_input)
        typewriter(result)