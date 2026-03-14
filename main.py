"""
main.py — Interactive voice agent CLI for Fitch structured finance reports.

Commands inside the loop:
    add     — paste a Fitch report URL to ingest it
    quit    — exit

Run:
    python main.py              # voice + text
    python main.py --no-voice   # text only
    python main.py --verbose    # show retrieved chunks
"""

import argparse

from dotenv import load_dotenv

load_dotenv()


def run(no_voice: bool = False, verbose: bool = False) -> None:
    from agent import answer
    from ingest import ingest_url

    if not no_voice:
        from voice import speak

    print("=" * 60)
    print("  Fitch Voice Agent — Structured Finance RAG")
    print("  Ask a question, or type 'add' to index a new report.")
    print("  Type 'quit' or press Ctrl-C to exit.")
    print("=" * 60)

    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not query:
            continue

        if query.lower() in {"quit", "exit", "q"}:
            print("Goodbye.")
            break

        if query.lower() == "add":
            url = input("Paste Fitch report URL: ").strip()
            if url:
                ingest_url(url)
            continue

        print("\nThinking...", flush=True)
        response = answer(query, verbose=verbose)
        print(f"\nAgent: {response}\n")

        if not no_voice:
            try:
                speak(response)
            except Exception as e:
                print(f"[voice error] {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fitch Ratings Voice Agent")
    parser.add_argument("--no-voice", action="store_true", help="Disable TTS output")
    parser.add_argument("--verbose", action="store_true", help="Print retrieved chunks")
    args = parser.parse_args()
    run(no_voice=args.no_voice, verbose=args.verbose)


if __name__ == "__main__":
    main()
