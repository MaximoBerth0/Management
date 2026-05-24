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
  initialize_stock()     
  add_stock()         
  remove_stock()       
  adjust_stock()        
  list_stock_movements() 
"""

from app.inventory.models.enums import StockMovementType
from app.inventory.models.stock import StockMovement
from app.inventory.repositories.category_repo import CategoryRepository
from app.inventory.repositories.location_repo import LocationRepository
from app.inventory.repositories.product_repo import ProductRepository
from app.inventory.repositories.stock_repo import StockRepository


class InventoryService: 
    def __init__(
        self,
        stock_repo: StockRepository,
        product_repo: ProductRepository,
        category_repo: CategoryRepository,
        location_repo: LocationRepository
      ): 
        self.stock_repo = stock_repo
        self.product_repo = product_repo
        self.category_repo = category_repo
        self.location_repo = location_repo

# product 
        
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
    
# category 

    async def create_category(self, name: str, description: str):
      if not name or not name.strip():
        raise ValueError("category name is required")
    
      if not description or not description.strip():
        raise ValueError("category description is required")
    
      name = name.strip()
      description = description.strip()
    
      existing = await self.category_repo.get_by_name(name)
      if existing:
        raise ValueError(f"category '{name}' already exists")
    
      return await self.category_repo.create_category(name, description)
    
    async def remove_category(self, category_id: int):
      return await self.category_repo.delete_category(category_id)

    async def add_product_to_category(self, product_id: int, category_id: int):
      category = await self.category_repo.get_category(category_id)
      if not category:
        raise ValueError(f"Category with ID {category_id} not found")
    
      product = await self.product_repo.get_product(product_id)
      if not product:
        raise ValueError(f"Product with ID {product_id} not found")
    
      if product not in category.products:
        category.products.append(product)
        await self.category_repo.save_category(category)  
    
      return category

# stock

    async def initialize_stock(self, location_id: int, product_id: int, quantity: int, reorder_point: int):
      location_id = abs(int(location_id))
      product_id = abs(int(product_id))
      quantity = abs(int(quantity))
      reorder_point = abs(int(reorder_point))
    
    # ensure reorder_point doesn't exceed quantity
      reorder_point = min(reorder_point, quantity)
    
      location = await self.location_repo.get_location(location_id)
      if not location:
        raise ValueError("invalid location id")
    
      product = await self.product_repo.get_product(product_id)
      if not product:
        raise ValueError("invalid product id")
    
      if quantity <= 0:
        raise ValueError("quantity must be > 0")
    
      return await self.stock_repo.initialize_stock(location_id, product_id, quantity, reorder_point)

    async def add_stock(self, product_id, location_id, quantity, user_id):
      stock = await self.stock_repo.get_stock_by_location_and_product(product_id, location_id)
      if not stock:
        raise ValueError("Invalid product or location id")
      
      previous_quantity = stock.quantity 

      stock.quantity += quantity
      new_quantity = stock.quantity

      movement = StockMovement(
        stock_id=stock.id, 
        movement_type=StockMovementType.IN,
        quantity=quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        created_by=user_id
    )
      await self.stock_repo.update_quantity_stock(stock)      
      await self.stock_repo.create_movement(movement) 
    
      return movement
    
    async def remove_stock(self, product_id, location_id, quantity, user_id): 
      stock = await self.stock_repo.get_stock_by_location_and_product(product_id, location_id)
      if not stock:
        raise ValueError("Invalid product or location id")
      
      if stock.quantity < quantity:
        raise ValueError("stock cannot be negative")
      
      previous_quantity = stock.quantity 

      stock.quantity -= quantity
      new_quantity = stock.quantity

      movement = StockMovement(
        stock_id=stock.id, 
        movement_type=StockMovementType.OUT,
        quantity=quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        created_by=user_id
    )
      await self.stock_repo.update_quantity_stock(stock)      
      await self.stock_repo.create_movement(movement) 
    
      return movement
    
    async def adjust_stock(self, product_id, location_id, quantity, user_id): 
      stock = await self.stock_repo.get_stock_by_location_and_product(product_id, location_id)
      if not stock:
        raise ValueError("Invalid product or location id")
    
      if quantity < 0:  
        raise ValueError("stock cannot be negative")
    
      previous_quantity = stock.quantity 
      stock.quantity = quantity 
      new_quantity = stock.quantity
    
      movement = StockMovement(
        stock_id=stock.id, 
        movement_type=StockMovementType.ADJUST,
        quantity=abs(new_quantity - previous_quantity),  # store the difference
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        created_by=user_id
      )
    
      await self.stock_repo.update_quantity_stock(stock)      
      await self.stock_repo.create_movement(movement)
      return movement
    
    async def list_stock_movements(self, stock_id: int, limit: int = 100):
      stock = await self.stock_repo.get_stock(stock_id)
      if not stock:
        raise ValueError(f"Stock with ID {stock_id} not found")

      return await self.stock_repo.list_stock_movements(stock_id, limit)
