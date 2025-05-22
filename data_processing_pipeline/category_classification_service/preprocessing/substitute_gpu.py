import re, os

class ReplaceText:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        gpu_names_txt_path = os.path.join(base_dir, '..', 'datasets', 'gpu_names.txt')

        with open(gpu_names_txt_path, 'r') as f:
            gpu_names = [line.strip() for line in f if line.strip()]
            escaped_gpu_names = [re.escape(name) for name in gpu_names]
            self.gpu_pattern = r'\b(?:' + '|'.join(escaped_gpu_names) + r')\b'
        
    def substitute(self, rawtext):
        gpu_pattern = self.gpu_pattern
        pattern = re.compile(gpu_pattern, flags=re.IGNORECASE)

        return pattern.sub('[gpu]', rawtext)