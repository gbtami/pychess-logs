import asyncio
import os
import sys

if sys.platform not in ("win32", "darwin"):
    import uvloop
else:
    print("uvloop not installed")

from aiohttp import web

if sys.platform not in ("win32", "darwin"):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


async def logs(request):
    data = await request.post()
    print("LOG POSTED:")
    for key, item in data.items():
        print(key, item)
    return web.Response()


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post('/', logs)])
    web.run_app(app, access_log=None, port=int(os.environ.get("PORT", 8080)))