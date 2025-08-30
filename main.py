from dotenv import load_dotenv
from honcho import Honcho
import os

_ = load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")


# Initialize client (uses demo environment and default workspace)
client = Honcho()

alice = client.peer("alice")
bob = client.peer("bob")

session = client.session("session_1")
session.add_peers([alice, bob])

session.add_messages(
    [
        alice.message("Hi Bob, how are you?"),
        bob.message("I'm good, thank you!"),
        alice.message("What are you doing today after work?"),
        bob.message("I'm going to the gym! I've been trying to get back in shape."),
        alice.message("That's great! I should probably start exercising too."),
        bob.message("You should! I find that evening workouts help me relax."),
    ]
)

response = alice.chat("Tell me about Bob's interests and habits")
print(response)
