from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Extract real client IP from request headers.
    Checks Cloudflare headers first, then falls back to standard headers.

    Used since this api is running on a pod behind a reverse proxy and
    cloudflare tunnel.

    Returns:
        The client IP address as a string
    """
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    if request.client:
        return request.client.host

    return "unknown"
