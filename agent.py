import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv
from openai import OpenAI


@dataclass
class SimpleAIAgent:
    model: str
    system_prompt: str

    def __post_init__(self) -> None:
        self._client = OpenAI()

    def ask(self, user_message: str) -> str:
        response = self._client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.output_text.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a simple AI agent from the terminal.")
    parser.add_argument("--message", "-m", help="Single prompt to send to the agent.")
    return parser


def run_chat_loop(agent: SimpleAIAgent) -> None:
    print("Simple AI Agent is ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bye!")
            return
        if not user_input:
            continue
        print(f"Agent: {agent.ask(user_input)}\n")


def main() -> None:
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set. Add it to your environment or .env file.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    system_prompt = (
        "You are a concise and helpful assistant. "
        "Give practical answers with short examples when useful."
    )
    agent = SimpleAIAgent(model=model, system_prompt=system_prompt)

    args = build_parser().parse_args()
    if args.message:
        print(agent.ask(args.message))
    else:
        run_chat_loop(agent)


if __name__ == "__main__":
    main()
