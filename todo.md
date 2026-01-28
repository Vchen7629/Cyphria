1. update frontend search bar on header to use debounce by 300 ms to delay api calls on each search keystroke to avoid bloating our valkey caching layer
2. Look into adding manual cache invalidation in data pipeline services
3. Add rate limiting either on the fastapi insights api itself or via kubernetes gateway api
4. Other improvements to make the caching/insights api more robust

5. Add a service in the processing pipeline that checks the prices of all products in a topic and time window on amazon
and writes to a prices table