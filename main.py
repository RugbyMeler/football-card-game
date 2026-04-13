"""Football Card Game — entry point."""
print("BOOT")  # must appear in console if Python runs at all
import sys
import asyncio
print("BOOT: asyncio imported")

try:
    from graphics.app import App
    print("BOOT: App imported OK")
except Exception as e:
    print(f"BOOT: App import FAILED: {e}")
    import traceback
    traceback.print_exc()
    App = None


async def main() -> None:
    print("BOOT: main() called")
    if App is None:
        print("BOOT: cannot start, App failed to import")
        return
    try:
        await App().run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FATAL: {e}")


asyncio.run(main())
