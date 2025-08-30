from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from honcho import Honcho, Session
import discord
import os

_ = load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

workspace_id = "foobar"
session_id = "session1"
# Initialize client (uses demo environment and default workspace)
honcho_client = Honcho(workspace_id=workspace_id)


openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY
)

MODEL_NAME = "openai/gpt-4o"

assistant = honcho_client.peer(id="assistant", config={"observe_me": False})


def llm(name: str, session: Session, prompt) -> str:
    """
    Call the LLM with the given prompt and chat history.

    You should expand this function with custom logic, prompts, etc.
    """
    messages: list[dict[str, object]] = session.get_context(summary=False).to_openai(
        assistant=assistant
    )

    # char_messages = session.get_messages(filters={"peer_id": name})
    # print(f"DEBUGPRINT[38]: main.py:38: char_messages={char_messages}")
    # char_messages.append({"role": "user", "content": prompt})
    # for m in messages:
    #     print(f"DEBUGPRINT[37]: main.py:37: messages={m}")

    char_messages = []

    for m in messages:
        if m.get("name") == name:
            char_messages.append(m)

    try:
        completion = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=char_messages,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(e)
        return f"Error: {e}"


def init_honcho_session():
    return honcho_client.session(session_id)

    # peers = honcho_client.get_peers()
    #
    # print(f"DEBUGPRINT[31]: main.py:22: peers={peers}")
    #
    # alice = honcho_client.peer("alice")
    # bob = honcho_client.peer("bob")
    # session.add_peers([alice, bob])
    #
    # session.add_messages(
    #     [
    #         alice.message("Hi Bob, how are you?"),
    #         bob.message("I'm good, thank you!"),
    #         alice.message("What are you doing today after work?"),
    #         bob.message("I'm going to the gym! I've been trying to get back in shape."),
    #         alice.message("That's great! I should probably start exercising too."),
    #         bob.message("You should! I find that evening workouts help me relax."),
    #     ]
    # )
    #
    # response = alice.chat("Tell me about Bob's interests and habits")
    # print(response)


discord_bot = discord.Bot()


@discord_bot.event
async def on_ready():
    print(f"{discord_bot.user} is ready and online!")


def read_text_files_pathlib(directory):
    chars_dir = Path(directory)
    file_contents = {}

    # Read all .txt files
    for filepath in chars_dir.glob("*.txt"):
        try:
            file_contents[filepath.stem] = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {filepath.name}: {e}")

    return file_contents


# MAIN
def main():
    chars_data = read_text_files_pathlib("characters/")

    session = init_honcho_session()

    for name, sheet in chars_data.items():
        peer = honcho_client.peer(name)
        session.add_messages(
            [
                peer.message("Respond as if you are the following character."),
                peer.message(sheet),
            ]
        )

        @discord_bot.slash_command(name=name, description=f"Message {name}")
        async def message(ctx: discord.ApplicationContext, message: str):
            await ctx.defer()  # Tell Discord we're working on it
            initial_message = f"> {message}\n"
            llm_response = llm(name, session, message)
            response = initial_message + llm_response
            await ctx.followup.send(response)  # Send as follow-up instead of respond

    discord_bot.run(DISCORD_BOT_TOKEN)  # run the bot with the token


main()
