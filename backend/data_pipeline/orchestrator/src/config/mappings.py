# maps a category to a list of product topics
CATEGORYTOPIC = {
    "COMPUTING": ["GPU", "LAPTOP", "CPU", "MONITOR", "MECHANICAL KEYBOARD"],
    "AUDIO": ["HEADPHONE", "EARBUD", "SOUNDBAR", "DAC", "SPEAKER"],
    "MOBILE": ["SMARTPHONE", "TABLET"],
    "GAMING": ["GAMING MICE", "CONTROLLER", "GAMING HEADESET", "GAMING LAPTOP"],
    "PHOTOGRAPHY": ["CAMERA", "LENSE", "TRIPOD", "CAMERA BAG"],
    "KITCHEN": ["ESPRESSO MACHINE", "MICROWAVE", "AIR FRYER", "BLENDER", "TOASTER", "RICE COOKER", "COOKWARE", "PIZZA OVEN", "KNIFE", "REFRIDGERATOR", "DISHWASHER", "WATER FILTER"],
    "CLEANING AND LAUNDRY": ["ROBOT VACUUM", "VACUUM CLEANER", "WASHING MACHINE" "CLOTHES DRYER", "AIR PURIFIER", "HUMIDIFIER"],
    "SMART HOME": ["SMART THERMOSTAT", "VIDEO DOORBELL"],
    "BED AND BATH": ["MATTRESS", "PILLOW", "BIDET"],
    "OUTDOOR": ["PELLET GRILL", "SLEEPING BAG", "TENT", "COOLER"],
    "GROOMING AND BEAUTY": ["RAZOR", "SHAVING CREAM", "SHAVING SOAP", "AFTERSHAVE", "SHAVING BLADE", "CLEANSER", "MOISTURIZER", "SUNSCREEN", "PERFUME", "COLOGNE", "MAKEUP"],
    "FITNESS": ["SQUAT RACK", "EXERCISE BIKE", "TREADMILL", "ROWING MACHINE", "DUMBELL", "KETTLEBELL"],
    "AUTO": ["DASH CAM", "RADAR DETECTOR", "PHONE HOLDER"]
}

# maps a product topic to a list of subreddits to fetch from
TOPICSUBREDDIT = {
    # Computing subreddits
    "GPU": ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"],
    "LAPTOP": [
        "laptops", "gaminglaptops", "AcerOfficial", "macbookair", "macbookpro", "asus", "Dell", 
        "Hewlett_Packard", "Lenovo", "Surface", "Razer", "GalaxyBook", "System76"
    ],
    "CPU": ["amd", "Intel", "buildapc", "gamingpc", "pcbuild", "hardware"],
    "MONITOR": [
        "Monitors", "buildapc", "buildapcmonitors", "ultrawidemasterrace", "gamingpc", 
        "pcbuild", "hardware", "OLED_Gaming"
    ],
    "MECHANICAL KEYBOARD": [
        "MechanicalKeyboards", "olkb", "keyboards", "HHKB", "CustomKeyboards", "BudgetKeebs", 
        "LogitechG", "HyperX", "Razer", "steelseries", "WootingKB", "Keychron", "NuPhy"
    ],

    # Audio subreddits
    "HEADPHONE": [
        "headphones", "HeadphoneAdvice", "Audiophile", "BudgetAudiophile", "Airpodsmax",
        "beatsbydre", "bose", "JBL", "Sennheiser", "SonyHeadphones",
    ],
    "EARBUD": [
        "Earbuds", "Audiophile", "BudgetAudiophile", "Airpods", "beatsbydre", "JBL",
        "SonyHeadphones", "bose", "Jlab", "Soundcore"
    ],
    "SOUNDBAR": ["Soundbars", "hometheater", "Audiophile", "BudgetAudiophile"],
    "DAC": ["headphones", "HeadphoneAdvice", "Audiophile", "BudgetAudiophile", "StereoAdvice"],
    "SPEAKER": ["Bluetooth_speakers", "SoundSystem", "StereoAdvice", "Audiophile", "BudgetAudiophile"],

    # Mobile subreddits
    "SMARTPHONE": ["Smartphones", "Android", "PickAnAndroidForMe", "iPhone"],
    "TABLET": ["AndroidTablets", "ipad", "tablets"],

    # Gaming subreddits
    "GAMING MICE": ["MouseReview"],
    "CONTROLLER": ["Controller", "XboxController", "SteamController"],
    "GAMING HEADSET": ["Gaming_Headsets"],
    "GAMING LAPTOP": ["GamingLaptops", "SuggestALaptop", "LaptopDeals", "PCMasterRace"],

    # Photography subreddits
    "CAMERA": ["cameras", "photography", "Photography_Gear", "canon", "nikon", "SonyAlpha", "fujifilm", "fujifilmX", "Lumix", "Leica", "pentax", "olympuscamera", "DSLR"],
    "LENSE": ["cameras", "photography", "Photography_Gear", "canon", "nikon", "SonyAlpha", "fujifilm", "Lumix", "Leica", "pentax", "olympuscamera"],
    "TRIPOD": ["photography", "Photography_Gear"],
    "CAMERA BAG": ["CameraBags", "ManyBaggers", "Photography_Gear", "AskPhotography"],

    # Kitchen subreddits
    "ESPRESSO MACHINE": ["espresso", "coffee", "Nespresso", "superautomatic", "LaPavoniLovers"],
    "MICROWAVE": ["Appliances", "BuyItForLife", "ApplianceAdvice"],
    "AIR FRYER": ["PoweredByExperience", "airfryer", "BuyItForLife", "Appliances"],
    "BLENDER": ["Vitamix", "Blendtec", "BuyItForLife", "Appliances", "Smoothies", "BudgetFood"],
    "TOASTER": ["BuyItForLife", "Appliances", "Cooking"],
    "RICE COOKER": ["ricecookers", "RiceCookerRecipes", "zojirushi", "Cuckoo", "BuyItForLife", "Appliances", "Cooking"],
    "COOKWARE": ["cookware", "carbonsteel", "castiron", "StainlessSteelCooking"],
    "PIZZA OVEN": ["PizzaOvens", "ooni", "GozneyDome", "Pizza", "neapolitanpizza", "BestPizzaOven", "Cooking", "Appliances", "OutdoorKitchens"],
    "KNIFE": ["chefknives", "buyitforlife"],
    "REFRIDGERATOR": ["Appliances", "BuyItForLife", "KitchenRemodel", "ApplianceAdvice"],
    "DISHWASHER": ["Appliances", "BuyItForLife", "dishwashers", "ApplianceAdvice"],
    "WATER FILTER": ["BuyItForLife", "WaterTreatment", "HydroHomies"],

    # Cleaning and laundry subreddits
    "ROBOT VACUUM": ["RobotVacuums", "Roomba", "EcoVacs", "BuyItForLife"],
    "VACUUM CLEANER": ["VacuumCleaners", "BuyItForLife"],
    "WASHING MACHINE": ["Appliances", "BuyItForLife", "laundry", "CleaningTips"],
    "CLOTHES DRYER": ["Appliances", "BuyItForLife", "laundry", "CleaningTips"],
    "AIR PURIFIER": ["AirPurifiers", "Allergy", "BuyItForLife"],
    "HUMIDIFIER": ["Humidifiers", "BuyItForLife", "hvacadvice", "Houseplants"],

    # Smart home subreddits
    "SMART THERMOSTAT": ["hvacadvice", "homeassistant", "smarthome", "Nest", "ecobee", "thermostats"],
    "VIDEO DOORBELL": ["homesecurity", "homeassistant", "smarthome", "Homekit", "EufyCam", "Ubiquiti", "Ring", "reolinkcam", "SecurityCamera", "homedefense"],

    #! Bed and bath subreddits
    "MATTRESS": ["Mattress", "bedroom", "wellmadebeds", "Bedding", "BuyItForLife", "Sleep"],
    "PILLOW": ["Bedding", "BuyItForLife", "Pillow", "Sleep"],
    "BIDET": ["bidets", "hygiene", "hemorrhoid", "plumbing"],

    # Outdoor subreddits
    "PELLET GRILL": ["pelletgrills", "smoking", "BBQ", "grilling", "Smokingmeat", "Traeger", "griddling", "Buyitforlife", "recteq", "UKBBQ", "PitBossGrills"],
    "SLEEPING BAG": ["Ultralight", "CampingGear", "backpacking", "hiking", "camping", "hikinggear", "alpinism", "hiking", "camping"],
    "TENT":  ["Ultralight", "CampingGear", "backpacking", "hiking", "camping", "hikinggear", "hiking", "camping"],
    "COOLER": ["Coolers", "camping", "YetiCoolers"],

    # Grooming and beauty subreddits
    "RAZOR": ["wicked_edge", "Wetshaving", "shaving", "buyitforlife"],
    "SHAVING CREAM": ["shaving", "wicked_edge", "Wetshaving"],
    "SHAVING SOAP": ["shaving", "wetshaving", "wicked_edge"],
    "AFTERSHAVE": ["shaving", "wetshaving", "wicked_edge"],
    "SHAVING BLADE": ["shaving", "wetshaving", "wicked_edge"],
    "CLEANSER": ["SkincareAddiction", "Skincare_addiction", "30PlusSkinCare", "SkincareAddicts", "Acne", "45PlusSkinCare", "scajdiscussion", "hygiene", "beauty"],
    "MOISTURIZER": ["SkincareAddiction", "Skincare_addiction", "30PlusSkinCare", "SkincareAddicts", "Acne", "45PlusSkinCare", "scajdiscussion", "hygiene", "beauty"],
    "SUNSCREEN":  ["SkincareAddiction", "Skincare_addiction", "30PlusSkinCare", "SkincareAddicts", "45PlusSkinCare", "scajdiscussion", "beauty"],
    "PERFUME": ["Beauty", "Perfumes", "Fragrance", "Perfumesthatfeellike", "FragranceStories", "ScentHeads", "FemFragLab"],
    "COLOGNE": ["Beauty", "Colognes", "Fragrance", "Perfumesthatfeellike", "FragranceStories", "ScentHeads"],
    "MAKEUP": ["MakeupAddiction", "BeautyAddiction", "MakeupAddicts", "Beauty", "AsianBeauty"],

    # Fitness subreddits
    "SQUAT RACK": ["homegym", "garagegym", "workout", "gainit", "BuyItForLife", "buyitforlifetips", "weightlifting", "powerlifting", "crossfit", "startingstrength"],
    "EXERCISE BIKE": ["cycling", "pelotoncycle", "SpinClass", "Zwift", "workout", "loseit", "OnePelotonRealSub", "IndoorCycling", "BuyItForLife", "buyitforlifetips"],
    "TREADMILL": ["treadmills", "xxrunning", "buyitforlife", "running", "ultramarathon", "beginnerfitness", "buyitforlifetips", "workout", "garagegym", "homegym"],
    "ROWING MACHINE": ["rowing", "garagegym", "beginnerfitness", "workout", "buyitforlife", "homegym", "BuyItForLife", "buyitforlifetips"],
    "DUMBELL": ["homegym", "garagegym", "workout", "BuyItForLife", "buyitforlifetips", "crossfit", "fitness30plus"],
    "KETTLEBELL": ["kettlebells", "kettlebell", "homegym", "garagegym", "BuyItForLife", "buyitforlifetips"],

    # Auto subreddits
    "DASH CAM": ["dashcam", "dashcams", "Truckers", "askcarguys", "CarsIndia", "Dashcamindia", "DubaiPetrolHeads", "drivingUK"],
    "RADAR DETECTOR": ["radardetectors", "Truckers", "askcarguys", "AMG"],
    "PHONE HOLDER": ["phmotorcycles", "bicycling", "buyitforlife", "carplay", "magsafe"]
}