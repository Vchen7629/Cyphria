import os, re

class ReplaceText:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        vehicle_brands_txt_path = os.path.join(base_dir, '..', 'datasets', 'vehicle_brands.txt')

        with open(vehicle_brands_txt_path, 'r') as f:
            vehicle_brands = [line.strip() for line in f if line.strip()]
            escaped_vehicle_brands = [re.escape(brand) for brand in vehicle_brands]
            self.vehicle_brand_pattern = r'\b(?:' + '|'.join(escaped_vehicle_brands) + r')\b'
    
    def substitute(self, rawtext):
        vehicle_brand_pattern = self.vehicle_brand_pattern
        pattern = re.compile(vehicle_brand_pattern, flags=re.IGNORECASE)

        return pattern.sub('[vehicleBrand]', rawtext)