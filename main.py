"""Football Card Game — entry point.

Run with:   python main.py          (graphical, default)
            python main.py --text   (original text mode)
            python -m pygbag .      (build for web)
"""
import sys
import asyncio

# All imports must be at module level for pygbag/WASM compatibility
from graphics.app import App


async def main() -> None:
    try:
        await App().run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FATAL: {e}")


asyncio.run(main())
