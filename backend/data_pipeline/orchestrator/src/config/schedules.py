# runs every 1.5 hours, triggers a run of fetching
# posts for each category topics
INGESTSCHEDULES = {
    "COMPUTING": "0 0 * * *",
    "AUDIO": "30 1 * * *",
    "MOBILE": "0 3 * * *",
    "GAMING": "30 4 * * *",
    "PHOTOGRAPHY": "0 6 * * *",
    "KITCHEN": "30 7 * * *",
    "CLEANING AND LAUNDRY": "0 9 * * *",
    "SMART HOME": "30 10 * * *",
    "BED AND BATH": "0 12 * * *",
    "OUTDOOR": "30 13 * * *",
    "GROOMING AND BEAUTY": "0 15 * * *",
    "FITNESS": "30 16 * * *",
    "AUTO": "0 18 * * *"
}

# runs 20 mins after each ingestion run
RANKINGSCHEDULES = {
    "COMPUTING": "20 0 * * *",
    "AUDIO": "50 1 * * *",
    "MOBILE": "20 3 * * *",
    "GAMING": "50 4 * * *",
    "PHOTOGRAPHY": "20 6 * * *",
    "KITCHEN": "50 7 * * *",
    "CLEANING AND LAUNDRY": "20 9 * * *",
    "SMART HOME": "50 10 * * *",
    "BED AND BATH": "20 12 * * *",
    "OUTDOOR": "50 13 * * *",
    "GROOMING AND BEAUTY": "20 15 * * *",
    "FITNESS": "50 16 * * *",
    "AUTO": "20 18 * * *"
}

