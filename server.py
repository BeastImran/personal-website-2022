# This main.py will be used as the entry point for any request.
from sanic import Sanic
from sanic.response import file
import gzip
from io import BytesIO as IO
from sanic import html

from paths import domain, www_domain, port, assets_path, only_domain, only_www_domain, port

sources = f"{domain}:{port} {www_domain}:{port}"
gzip_cache = dict()
app = Sanic("HTTPS_BeastImran")


@app.on_request
async def vaildate_request_domain(request):
    host = request.headers.get('host', '').split(":")[0]

    if not (host == only_domain or host == only_www_domain):
        return html(f"<h1>This domain is being used to impersonate <a href=\"http://{only_domain}\">{only_domain}</a> or is something wrong. Please report this domain and any other realted info <a href=\"https://t.me/beastimran\">here</a>.</h1>")

    if request.path in gzip_cache:
        return gzip_cache[request.path]


@app.on_response
async def response_functions(request, response):
    response.headers["cache-control"] = "private, must-revalidate, max-age=2592000"
    response.headers["content-security-policy"] = f"default-src {sources}; object-src 'none'; worker-src 'none'; font-src {sources} data:; form-action {sources}"
    response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
    response.headers["x-frame-options"] = "SAMEORIGIN"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["access-control-allow-origin"] = "no"
    response.headers["content-length"] = len(response.body)

    if request.path.rsplit(".")[-1].lower() in ("woff2", "woff", "png", "jpeg", "jpg", "mp4", "webm"):
        gzip_cache[request.path] = response
        return response

    accept_encoding = request.headers.get(
        "Accept-Encoding", "") or request.headers.get("accept-encoding", "")

    if ("gzip" not in accept_encoding.lower()) or (response.status < 200 or response.status >= 300 or "Content-Encoding" in response.headers):
        gzip_cache[request.path] = response
        return response

    gzip_buffer = IO()
    gzip_file = gzip.GzipFile(mode="wb", fileobj=gzip_buffer)
    gzip_file.write(response.body)
    gzip_file.close()

    response.body = gzip_buffer.getvalue()
    response.headers["content-encoding"] = "gzip"
    response.headers["vary"] = "accept-encoding"
    response.headers["content-length"] = len(response.body)

    gzip_cache[request.path] = response
    return response


@app.get("/")
async def index(_):
    return await file("./index.html")


@app.get("/assets/<asset_path:path>")
async def assets(_, asset_path):
    return await file(assets_path + asset_path)


@app.route("/sitemap.xml")
async def sitemap(_):
    return await file('sitemap.xml')


@app.route("/google1ae25284ecc16fa9.html")
async def google_verification(_):
    return await file('google1ae25284ecc16fa9.html')


@app.route("/robots.txt")
async def robots_txt(_):
    return await file('robots.txt')


if __name__ == "__main__":
    app.run("127.0.0.1", 80, access_log=False, debug=False)
