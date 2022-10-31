from sanic.response import redirect
from sanic import Sanic

from env import only_domain, http, http_port


app = Sanic("HTTP_BeastImran")


@app.get("/<page_path:path>")
async def handler(_, page_path):
    return redirect(http + only_domain + page_path)


if __name__ == "__main__":
    app.run(only_domain, http_port, debug=False, access_log=True)
