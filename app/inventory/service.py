"""
PRODUCT:
  get_product()
  list_products()
  create_product()
  update_product()
  activate_product()         
  deactivate_product() 

CATEGORY:
  create_category()
  remove_category()
  add_product_to_category()        

STOCK:
  reserve_stock()             
  release_reservation()       
  fulfill_reservation()       
  create_stock_movement()
  list_stock_movements()    
  get_available_stock()       
  update_reserved_quantity()
  check_stock_availability()   
"""

from app.inventory.repositories.category_repo import CategoryRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.inventory.repositories.stock_repo import StockRepository


class InventoryService: 
    def __init__(
        self,
        stock_repo: StockRepository,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
      ): 
        self.stock_repo = stock_repo
        self.product_repo = product_repo
        self.category_repo = category_repo
        
    async def get_product(self, product_id: int):
      result = self.product_repo.get_product(product_id)
      return result 
    
    async def list_products(self):
       result = self.product_repo.list_products()
       return result 
    
    async def create_product(self, name: str, sku: str, category_id: int):
      if not name or not name.strip():
        raise ValueError("product name is required")
    
      if not sku or not sku.strip():
        raise ValueError("SKU is required")
    
      # normalize
      name = name.strip()
      sku = sku.strip().upper()
    
      existing = await self.product_repo.get_by_sku(sku)
      if existing:
        raise ValueError(f"product with SKU '{sku}' already exists")
    
      category_exists = await self.category_repo.get_category(category_id)
      if category_exists:
        raise ValueError("category does not exist")
    
      return await self.product_repo.create_product(name, sku, category_id)
    
    async def update_product(
      self,
      product_id: int,
      name: str | None = None,
      sku: str | None = None,
      ):
      if name is None and sku is None:
        raise ValueError("At least one field must be provided for update")
    
      if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Product name cannot be empty")
    
      if sku is not None:
        sku = sku.strip().upper()
        if not sku:
            raise ValueError("SKU cannot be empty")
        
        existing = await self.product_repo.get_by_sku(sku)
        if existing and existing.id != product_id:
            raise ValueError(f"Product with SKU '{sku}' already exists")
    
      product = await self.product_repo.update_product(product_id, name, sku)
      if not product:
        raise ValueError(f"Product with ID {product_id} not found")
    
      return product
       
    async def activate_product(self, product_id: int):
      activate = self.product_repo.activate_product(product_id)
      return activate
        
    async def deactivate_product(self, product_id):
       deactivate = self.product_repo.deactivate_product(product_id)
       return deactivate
    
