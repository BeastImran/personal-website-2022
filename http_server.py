from sanic.response import redirect
from sanic import Sanic

app = Sanic("HTTP_BeastImran")


@app.get("/<page_path:path>")
async def handler(_, page_path):
    return redirect("https://beastimran.com/" + page_path)


if __name__ == "__main__":
    app.run("localhost", 80, debug=False, access_log=True)
