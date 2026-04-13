"""Football Card Game — entry point.

Run with:   python main.py          (graphical, default)
            python main.py --text   (original text mode)
            python -m pygbag .      (build for web)
"""
print("=== main.py loading ===")
import sys
import asyncio
print("=== imports done ===")


async def main_graphical() -> None:
    print("=== importing App ===")
    from graphics.app import App
    print("=== creating App ===")
    app = App()
    print("=== App created, entering run loop ===")
    await app.run()
    print("=== App.run() returned ===")


def main_text() -> None:
    from game import ui
    from game.campaign import Campaign, load_campaign, delete_save

    while True:
        ui.clear_screen()
        ui.print_title()
        ui.print_main_menu()
        choice = ui.get_menu_choice(["1", "2", "3"])

        if choice == "1":
            save = load_campaign()
            if save:
                print("\n  A saved campaign already exists.")
                print("  [o] Overwrite  [b] Back")
                sub = ui.get_menu_choice(["o", "b"])
                if sub == "b":
                    continue
                delete_save()
            name = input("\n  Enter your manager name: ").strip() or "The Gaffer"
            Campaign.new(name).run()

        elif choice == "2":
            save = load_campaign()
            if save is None:
                print("\n  No saved campaign found.")
                ui.pause()
                continue
            Campaign.from_save(save).run()

        elif choice == "3":
            print("\n  See you on the pitch.\n")
            break


async def main() -> None:
    print("=== main() called ===")
    try:
        await main_graphical()
    except Exception as e:
        import traceback
        print(f"=== CRASH: {e} ===")
        traceback.print_exc()


print("=== calling asyncio.run ===")
asyncio.run(main())
