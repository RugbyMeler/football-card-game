"""Football Card Game — entry point."""
import sys
import os

# pygbag extracts game files to /assets in the WASM virtual filesystem.
# Ensure that directory is on sys.path so package imports work.
for _p in ("/assets", "/assets/data", os.path.dirname(__file__)):
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

print("BOOT sys.path:", sys.path[:4])
print("BOOT __file__:", __file__)

import asyncio

try:
    from graphics.app import App
    print("BOOT: App imported OK")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"BOOT: App import FAILED: {e}")
    App = None


async def main() -> None:
    print("BOOT: main() called")
    if App is None:
        return
    try:
        await App().run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FATAL: {e}")


asyncio.run(main())
