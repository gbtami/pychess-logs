import asyncio
import os
import sys

from aiohttp import web


async def logs(request):
    data = await request.read()
    msg_token = request.headers["Logplex-Drain-Token"]
    msg_count = request.headers["Logplex-Msg-Count"]
    print("Logplex-Msg-Count:", msg_count, msg_token)
    for line in data.decode().split("\n"):
        print(line)
    return web.Response()


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post('/', logs)])
    web.run_app(app, access_log=None, port=int(os.environ.get("PORT", 8080)))
