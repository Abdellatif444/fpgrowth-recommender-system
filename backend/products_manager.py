import json
import os
from werkzeug.utils import secure_filename

class ProductsManager:
    def __init__(self, data_file='data/products.json', upload_folder='frontend/images/products'):
        self.data_file = data_file
        self.upload_folder = upload_folder
        self.products = {}
        self._load_products()
        
        # Ensure upload directory exists
        os.makedirs(self.upload_folder, exist_ok=True)

    def _load_products(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
            except Exception as e:
                print(f"Error loading products: {e}")
                self.products = {}
        else:
            self.products = {}

    def _save_products(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.products, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving products: {e}")

    def get_all_products(self):
        return self.products

    def get_product(self, name):
        return self.products.get(name)

    def update_product(self, name, price, description, image_url=None):
        if name not in self.products:
            self.products[name] = {}
        
        self.products[name]['price'] = float(price)
        self.products[name]['description'] = description
        if image_url:
            self.products[name]['image'] = image_url
            
        self._save_products()
        return self.products[name]

    def save_image(self, file):
        if file:
            filename = secure_filename(file.filename)
            # Add timestamp to avoid duplicates/caching issues
            import time
            timestamp = int(time.time())
            filename = f"{timestamp}_{filename}"
            
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            
            # Return relative path for frontend
            return f"images/products/{filename}"
        return None

products_manager = ProductsManager()
