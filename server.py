# This main.py will be used as the entry point for any request.
from sanic import Sanic
from sanic.response import file, html
import gzip
from io import BytesIO as IO

from paths import domain, www_domain, only_domain, only_www_domain, port, assets_path

sources = f"{domain}:{port} {www_domain}:{port}"
app = Sanic("BeastImran")


async def authentic_domain(request):
    host = request.headers.get('host', '').replace(":" + str(port), '')
    return host == only_domain or host == only_www_domain


async def send_response(request, response):
    requested_file = request.path.rsplit(".")

    if await authentic_domain(request):
        accept_encoding = request.headers.get(
            "Accept-Encoding", "") or request.headers.get("accept-encoding", "")

        response.headers["content-length"] = len(response.body)

        if requested_file[-1] in ("woff2", "woff", "png", "jpeg", "jpg", "mp4", "webm"):
            return response

        if ("gzip" not in accept_encoding.lower()) or (response.status < 200 or response.status >= 300 or "Content-Encoding" in response.headers):
            return response

        gzip_buffer = IO()
        gzip_file = gzip.GzipFile(mode="wb", fileobj=gzip_buffer)
        gzip_file.write(response.body)
        gzip_file.close()

        response.body = gzip_buffer.getvalue()
        response.headers["content-encoding"] = "gzip"
        response.headers["vary"] = "accept-encoding"

        return response

    return html(f"<h1>This domain is being used to impersonate <a href=\"http://{only_domain}\">{only_domain}</a>. Please report this domain if necessary to respected authority.</h1>")


@app.middleware("response")
async def add_cache_tts_policy(_, response):
    response.headers["cache-control"] = "private, must-revalidate, max-age=60"
    response.headers["content-security-policy"] = f"default-src {sources}; object-src 'none'; worker-src 'none'; font-src {sources} data:; form-action {sources}"
    response.headers["referrer-policy"] = "strict-origin-when-cross-origin"
    response.headers["x-frame-options"] = "SAMEORIGIN"
    response.headers["x-xss-protection"] = "1; mode=block"
    response.headers["access-control-allow-origin"] = "no"


@app.get("/")
@app.get("/index")
@app.get("/index.html")
@app.get("/home")
@app.get("/home.html")
async def index(request):
    return await send_response(request=request, response=await file("./index.html"))


@app.get("/assets/<asset_path:path>")
async def assets(request, asset_path):
    return await send_response(request=request, response=await file(assets_path + asset_path))


@app.route("/sitemap.xml")
async def sitemap(_):
    return await file('sitemap.xml')


@app.route("/google1ae25284ecc16fa9.html")
async def google_verification(_):
    return await file('google1ae25284ecc16fa9.html')


@app.route("/robots.txt")
async def robots_txt(_):
    return await file('robots.txt')
