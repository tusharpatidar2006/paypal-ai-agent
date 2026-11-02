"""Product catalog for simulated marketplace."""
import json
from pathlib import Path
from typing import Optional
from decimal import Decimal

from cleanroom.models.contracts import Money


class Product:
    """Product in catalog."""
    
    def __init__(self, data: dict):
        """Initialize product from catalog data.
        
        Args:
            data: Product data dict
        """
        self.sku = data["sku"]
        self.merchant_id = data["merchant_id"]
        self.category = data["category"]
        self.title = data["title"]
        self.description = data["description"]
        self.price = Money(
            currency=data["price"]["currency"],
            value=Decimal(str(data["price"]["value"])),
        )
        self.features = data.get("features", [])
        self.rating = data.get("rating", 0.0)
        self.review_count = data.get("review_count", 0)


class Merchant:
    """Merchant in catalog."""
    
    def __init__(self, data: dict):
        """Initialize merchant from catalog data.
        
        Args:
            data: Merchant data dict
        """
        self.id = data["id"]
        self.name = data["name"]
        self.reputation = data.get("reputation", 3.0)


class Catalog:
    """Product catalog."""
    
    def __init__(self, catalog_path: Path | str = "fixtures/catalog.json"):
        """Load catalog from JSON file.
        
        Args:
            catalog_path: Path to catalog JSON
        """
        self.catalog_path = Path(catalog_path)
        self.products: dict[str, Product] = {}
        self.merchants: dict[str, Merchant] = {}
        self._load()
    
    def _load(self) -> None:
        """Load catalog from file."""
        if not self.catalog_path.exists():
            # Create default catalog
            self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
            return
        
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Load merchants
        for merchant_data in data.get("merchants", []):
            merchant = Merchant(merchant_data)
            self.merchants[merchant.id] = merchant
        
        # Load products
        for product_data in data.get("products", []):
            product = Product(product_data)
            self.products[product.sku] = product
    
    def get_product(self, sku: str) -> Optional[Product]:
        """Get product by SKU.
        
        Args:
            sku: Product SKU
            
        Returns:
            Product or None if not found
        """
        return self.products.get(sku)
    
    def get_merchant(self, merchant_id: str) -> Optional[Merchant]:
        """Get merchant by ID.
        
        Args:
            merchant_id: Merchant ID
            
        Returns:
            Merchant or None if not found
        """
        return self.merchants.get(merchant_id)
    
    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        merchant_id: Optional[str] = None,
    ) -> list[Product]:
        """Search products.
        
        Args:
            query: Search query
            category: Filter by category
            merchant_id: Filter by merchant
            
        Returns:
            List of matching products
        """
        results = []
        query_lower = query.lower()
        
        for product in self.products.values():
            # Skip honeypot items in normal search
            if "HONEYPOT" in product.sku:
                continue
            
            # Filter by category
            if category and product.category != category:
                continue
            
            # Filter by merchant
            if merchant_id and product.merchant_id != merchant_id:
                continue
            
            # Filter by query
            if query:
                if (
                    query_lower in product.title.lower()
                    or query_lower in product.description.lower()
                    or any(query_lower in feat.lower() for feat in product.features)
                ):
                    results.append(product)
            else:
                results.append(product)
        
        return results
    
    def is_honeypot(self, sku: str) -> bool:
        """Check if SKU is a honeypot item.
        
        Args:
            sku: Product SKU
            
        Returns:
            True if honeypot
        """
        return "HONEYPOT" in sku.upper()
