import gzip
import os
import logging.config

from aiohttp import web

class GZipRotator:
    def __call__(self, source, dest):
        os.rename(source, dest)
        with open(dest, 'rb') as f_in, gzip.open("%s.gz" % dest, 'wb') as f_out:
            f_out.writelines(f_in)
        os.remove(dest)

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            # "when": "S",
            # "interval": 1,
            "backupCount": 15,
            "filename": "./logs/pychess-variants.log",
            "encoding": "utf8"
        },
    },
    "loggers": {
        # root logger
        "my_logger": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)

log = logging.getLogger("my_logger")
log.handlers[0].rotator = GZipRotator()

async def logs(request):
    data = await request.read()
    # msg_token = request.headers["Logplex-Drain-Token"]
    # msg_count = request.headers["Logplex-Msg-Count"]
    # print("Logplex-Msg-Count:", msg_count, msg_token)
    for line in data.decode().split("\n"):
        if "host heroku router -" in line:
            # we want to completely skip lines like these, which are basically the access log from heroku web server:
            # 331 <134>1 2025-12-26T12:07:27.898551+00:00 host heroku router - at=info method=GET path="/static/chessground.css" host=asdasdasd request_id=ea6a6ea1-587d-fd93-95fd-b2617cf4ca6b fwd="" dyno=web.1 connect=0ms service=2ms status=304 bytes=0 protocol=http1.1 tls=true tls_version=unknown
            continue
        else:
            # we want to remove the prefix that comes from heroku/logplex in lines like these:
            # 160 <190>1 2025-12-26T12:07:27.672845+00:00 host app web.1 - 2025-12-26 12:07:27,672.672 [WARNING] Anon–XqbjtBZ1 jB0w33OM users:58 users.get() HGMuller NOT IN db
            x = line.split("host app web.1 - ")
            if len(x) > 1:
                # and we ignore lines that don't look like this at all, so only print if line.split succeeded
                log.info(x[1])
    return web.Response()


if __name__ == "__main__":
    app = web.Application()
    app.add_routes([web.post('/', logs)])
    web.run_app(app, access_log=None, port=int(os.environ.get("PORT", 8080)))
