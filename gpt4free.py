from g4f.client import Client

client = Client()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": ""}]
)
print(response.choices[0].message.content)











import asyncio
import threading

async def async_worker():
    await asyncio.sleep(1)
    print("Async work completed")

def run_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_worker())
    loop.close()

if __name__ == "__main__":
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=run_loop, args=(new_loop,))
    t.start()
    t.join()  # Assicurati che il thread finisca prima di chiudere il programma
