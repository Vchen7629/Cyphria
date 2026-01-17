"""Category mapping used in the dags to inject the category/subreddits to fetch/process from"""

class CategoryMappings:
    CATEGORIES = ['GPU', 'LAPTOP', 'HEADPHONE']

    CATEGORY_SCHEDULES = {
        'GPU': '0 0 * * *', # Runs at 00:00
        'LAPTOP': '0 1 * * *', # Runs at 01:00
        'HEADPHONE': '0 2 * * *' # Runs at 02:00
    }
    RANKING_SCHEDULES = {
        'GPU': '30 0 * * *',  # Runs at 00:30
        'LAPTOP': '30 1 * * *',  # Runs at 01:30
        'HEADPHONE': '30 2 * * *'  # Runs at 02:30
    }
    CATEGORY_SUBREDDITS = {
        "GPU": ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"]
    }