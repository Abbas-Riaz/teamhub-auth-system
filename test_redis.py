# test_redis.py
import redis

r = redis.Redis(
    host="expert-kit-16405.upstash.io",
    port=6379,
    password="AUAVAAIncDIwZTAxNDNkM2RmNmI0Y2Y5YTllNWI0ZjE1YmQzZmZlMHAyMTY0MDU",
    ssl=True,
    ssl_cert_reqs=None,
)

r.set("test", "hello")
print(r.get("test"))  # Should print: b'hello'
