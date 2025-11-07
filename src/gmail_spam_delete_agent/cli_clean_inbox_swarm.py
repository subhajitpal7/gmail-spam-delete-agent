import argparse
import os
import sys
from dotenv import load_dotenv
from swarm_app import build_swarm, GmailAgentResponse


def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Missing GOOGLE_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="💌 Gmail Swarm — Simple Conversational Inbox Cleaner"
    )
    parser.add_argument(
        "--thread",
        default="default",
        help="Conversation thread ID to maintain context across turns.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only simulate deletions; do not actually remove emails.",
    )
    args = parser.parse_args()

    # Optional safety mode
    if args.dry_run:
        os.environ["DRY_RUN"] = "1"

    # 🧠 Build the Gmail agent executor
    app = build_swarm()

    # Memory configuration
    config = {"configurable": {"thread_id": args.thread},"recursion_limit": 1000}

    print("\n📬 Gmail Swarm Agent is live!")
    print("💬 Chat naturally about your inbox. Example:")
    print("   - 'Show me unread promotional emails'")
    print("   - 'Delete emails older than 30 days'")
    print("💡 Type 'exit' or 'quit' to end the session.\n")

    # Conversation history for continuity
    messages = []

    try:
        while True:
            user_input = input("🧠 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Exiting Gmail Swarm session. Goodbye!")
                break

            messages.append({"role": "user", "content": user_input})

            try:
                # Invoke agent and get structured response
                result = app.invoke({"messages": messages}, config)
                response: GmailAgentResponse = result["structured_response"]

                print(f"\n🤖 Agent: {response.message}")
                if not response.success:
                    print(f"⚠️ Tool Error: {response.error_type or 'Unknown'}")
                    if response.error_message:
                        print(f"   Detail: {response.error_message}")

            except Exception as e:
                print(f"⚠️  Error: {e}\n")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Exiting session.")


if __name__ == "__main__":
    main()
