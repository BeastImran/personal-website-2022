from sanic import Sanic
from sanic.response import file, html, redirect
import gzip
from io import BytesIO as IO

from env import *

port_is_use = ssl_port if PROD else http_port

sources = f"{domain}:{port_is_use} {www_domain}:{port_is_use}"
app = Sanic("HTTPS_BeastImran")


@app.on_request
async def request_functions(request):
    if request.server_name != only_domain:
        return html(
            f'This is the real website: <a href="{domain}:{port_is_use}">{domain}</a>'
        )

    if PROD and request.server_port != 443:
        return redirect(f"https://{request.server_name}{request.path}", status=308)


@app.on_response
async def response_functions(request, response):
    response.headers["cache-control"] = "private"
    response.headers[
        "content-security-policy"
    ] = f"style-src {sources}; script-src {sources}; object-src 'none'; worker-src 'none'; font-src {sources} data:; form-action {sources}"
    response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
    response.headers["x-frame-options"] = "SAMEORIGIN"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["access-control-allow-origin"] = "no"
    response.headers["content-length"] = len(response.body)

    if PROD:
        response.headers["strict-transport-security"] = "max-age=3600"

    if request.path.rsplit(".")[-1].lower() in (
        "woff2",
        "woff",
        "png",
        "jpeg",
        "jpg",
        "mp4",
        "webm",
    ):
        return response

    accept_encoding = request.headers.get("Accept-Encoding", "") or request.headers.get(
        "accept-encoding", ""
    )

    if ("gzip" not in accept_encoding.lower()) or (
        response.status < 200
        or response.status >= 300
        or "Content-Encoding" in response.headers
    ):
        return response

    gzip_buffer = IO()
    gzip_file = gzip.GzipFile(mode="wb", fileobj=gzip_buffer)
    gzip_file.write(response.body)
    gzip_file.close()

    response.body = gzip_buffer.getvalue()
    response.headers["content-encoding"] = "gzip"
    response.headers["vary"] = "accept-encoding"
    response.headers["content-length"] = len(response.body)

    return response


@app.get("/")
async def index(_):
    return await file("./index.html")


@app.get("/assets/<asset_path:path>")
async def assets(_, asset_path):
    return await file(assets_path + asset_path)


@app.route("/sitemap.xml")
async def sitemap(_):
    return await file("sitemap.xml")


@app.route("/google1ae25284ecc16fa9.html")
async def google_verification(_):
    return await file("google1ae25284ecc16fa9.html")


@app.route("/robots.txt")
async def robots_txt(_):
    return await file("robots.txt")


if __name__ == "__main__":
    if PROD:
        app.prepare(
            host=only_domain,
            port=ssl_port,
            version=3,
            ssl=ssl_path,
            access_log=False,
            debug=False,
        )

        app.prepare(
            host=only_domain,
            port=ssl_port,
            version=1,
            ssl=ssl_path,
            access_log=False,
            debug=False,
        )
    else:
        app.prepare(only_domain, http_port, access_log=False, debug=True)

    Sanic.serve()
