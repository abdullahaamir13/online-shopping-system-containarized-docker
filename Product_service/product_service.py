from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List
import logging
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://p229221:22pseproject@projectcluster.amjkwy6.mongodb.net/?retryWrites=true&w=majority&appName=ProjectCluster"
client = MongoClient(MONGO_URI)
db = client["ProductService"]
products_collection = db["products"]

# Pydantic model for Product
class Product(BaseModel):
    id: str
    name: str
    stock: int
    price: float

# Pydantic model for Inventory Update
class InventoryUpdate(BaseModel):
    quantity: int

@app.get("/products", response_model=List[Product])
async def get_products():
    products = list(products_collection.find({}, {"_id": 0}))
    logger.info("Retrieved all products")
    return products

@app.post("/products")
async def add_product(product: Product):
    existing_product = products_collection.find_one({"id": product.id})
    if existing_product:
        logger.warning(f"Product ID {product.id} already exists")
        raise HTTPException(status_code=400, detail="Product ID already exists")
    products_collection.insert_one(product.dict())
    logger.info(f"Product added: {product.id}")
    return {"id": product.id, "message": "Product added"}

@app.put("/products/{product_id}")
async def update_product(product_id: str, product: Product):
    existing_product = products_collection.find_one({"id": product_id})
    if not existing_product:
        logger.warning(f"Product ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = {k: v for k, v in product.dict().items() if k in ["name", "stock", "price"]}
    result = products_collection.update_one({"id": product_id}, {"$set": update_data})
    if result.modified_count == 0:
        logger.info(f"No changes made to product {product_id}")
        return {"id": product_id, "message": "No changes detected"}
    logger.info(f"Product updated: {product_id}")
    return {"id": product_id, "message": "Product updated"}

@app.get("/inventory/{product_id}")
async def check_inventory(product_id: str, quantity: int):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    product = products_collection.find_one({"id": product_id}, {"_id": 0})
    if not product:
        logger.warning(f"Product ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    available = product["stock"] >= quantity
    logger.info(f"Checked inventory for product {product_id}: available={available}")
    return {"id": product_id, "available": available, "stock": product["stock"]}

@app.put("/inventory/{product_id}")
async def update_inventory(product_id: str, update: InventoryUpdate):
    if update.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    product = products_collection.find_one({"id": product_id})
    if not product:
        logger.warning(f"Product ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    new_stock = product["stock"] - update.quantity
    if new_stock < 0:
        logger.warning(f"Insufficient stock for product {product_id}")
        raise HTTPException(status_code=400, detail="Insufficient stock")
    products_collection.update_one({"id": product_id}, {"$set": {"stock": new_stock}})
    logger.info(f"Updated inventory for product {product_id}: new_stock={new_stock}")
    return {"id": product_id, "new_stock": new_stock}

@app.delete("/products/clear")
async def clear_products():
    result = products_collection.delete_many({})
    logger.info(f"Cleared {result.deleted_count} products from the collection")
    return {"message": f"Deleted {result.deleted_count} products"}

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    result = products_collection.delete_one({"id": product_id})
    if result.deleted_count == 0:
        logger.warning(f"Product ID {product_id} not found")
        raise HTTPException(status_code=404, detail="Product not found")
    logger.info(f"Deleted product: {product_id}")
    return {"id": product_id, "message": "Product deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)