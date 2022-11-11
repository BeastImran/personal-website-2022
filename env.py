PROD = False

only_domain = "localhost"
ssl_port = 443
http_port = 8000

http = "http://"
https = "https://"
domain = https if PROD else http + only_domain
www_domain = https if PROD else http + "www." + only_domain

assets_path = "./assets/min/"

ssl_path = {
    "cert": "/etc/letsencrypt/live/beastimran.com/fullchain.pem",
    "key": "/etc/letsencrypt/live/beastimran.com/privkey.pem",
}
