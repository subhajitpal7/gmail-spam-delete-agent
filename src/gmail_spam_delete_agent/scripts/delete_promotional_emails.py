import argparse
import os
import sys
from dotenv import load_dotenv
from gmail_spam_delete_agent import build_swarm, GmailAgentResponse

def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Missing GOOGLE_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="💌 Gmail Swarm — Simple Conversational Inbox Cleaner"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only simulate deletions; do not actually remove emails.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=100,
        help="The maximum number of emails to delete.",
    )
    args = parser.parse_args()

    # Optional safety mode
    if args.dry_run:
        os.environ["DRY_RUN"] = "1"

    # 🧠 Build the Gmail agent executor
    app = build_swarm()

    # Memory / runtime configuration
    config = {"configurable": {"thread_id": 1}, "recursion_limit": 1000}

    # merge streaming options
    streaming_opts = {
        "stream_mode": ["messages", "values"],  # use strings to avoid enum/version issues
        "stream_subgraphs": True,               # enable subgraph/token-by-token streaming
    }

    # merge (non-destructively)
    config_with_streaming = {**config, **streaming_opts}

    # Conversation history for continuity
    messages = []

    try:
        user_input = f"Delete {args.max_results} emails by skimming all the emails and list their subject lines."

        # add user message into the messages list the agent expects
        messages.append({"role": "user", "content": user_input})

        print(f"\n💬 User: {user_input}\n")
        
        # Stream instead of invoke to see intermediate steps
        for event in app.stream({"messages": messages}, config_with_streaming):
            # 1) node-update tuple: (node_name, updates)
            if isinstance(event, tuple) and len(event) == 2 and isinstance(event[0], str):
                node_name, updates = event
                print(f"📍 Node update: {node_name} -> {updates}")
                if isinstance(updates, dict) and "structured_response" in updates:
                    resp: GmailAgentResponse = updates["structured_response"]
                    print(f"🤖 Agent (from {node_name}): {resp.message}")

            # 2) full-state dict (common with "values")
            elif isinstance(event, dict):
                # structured_response may appear when the agent node updates
                if "structured_response" in event:
                    response: GmailAgentResponse = event["structured_response"]
                    print(f"\n🤖 Agent: {response.message}")
                    if not response.success:
                        print(f"⚠️ Tool Error: {response.error_type or 'Unknown'}")
                        if response.error_message:
                            print(f"   Detail: {response.error_message}")
                else:
                    # intermediate token/state chunk
                    print(f"📍 Intermediate state: {event}")

            else:
                print(f"📍 Unrecognized stream event: {event}")

    except Exception as e:
        print(f"⚠️ Error while streaming: {e}")


if __name__ == "__main__":
    main()