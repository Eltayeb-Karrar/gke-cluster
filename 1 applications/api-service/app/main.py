from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header, Request
from fastapi.responses import JSONResponse
from typing import Optional, List
import requests
import json
import os
import logging
import sys
import traceback
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel, Field, validator

# Configure structured logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

# Pydantic model for MongoDB ObjectId
class MongoModel(BaseModel):
    id: str = Field(..., alias="_id")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        
    @validator("id", pre=True)
    def convert_objectid_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

class Customer(MongoModel):
    name: str
    phone: str
    photo: str

app = FastAPI()

# Middleware to log requests and responses
@app.middleware("http")
async def log_request_middleware(request: Request, call_next):
    logger.info(f"Request started: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Request finished: {request.method} {request.url.path} with status {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {request.method} {request.url.path} with error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"}
        )

# Generic exception handler
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/api-service")
client = MongoClient(MONGO_URI)
db = client.get_database()
customers_collection = db.customers

IAM_SERVICE_URL = os.environ.get("IAM_SERVICE_URL", "http://iam-service:3001")
IMAGE_SERVICE_URL = os.environ.get("IMAGE_SERVICE_URL", "http://image-service:3002")

# Dependency to validate token with IAM service
def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    logger.info("Validating token with IAM service")
    try:
        response = requests.post(f"{IAM_SERVICE_URL}/validate", json={"token": token})
        response.raise_for_status()
        logger.info("Token validation successful")
        return response.json()["user"]
    except requests.exceptions.HTTPError as e:
        logger.error(f"Token validation failed: {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail="Invalid token")
    except Exception as e:
        logger.error(f"An unexpected error occurred during token validation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during token validation")

@app.get("/customers", response_model=List[Customer])
async def get_all_customers(skip: int = 0, limit: int = 10, current_user: dict = Depends(get_current_user)):
    logger.info(f"Getting all customers with skip={skip} and limit={limit}")
    customers = customers_collection.find().skip(skip).limit(limit)
    return [Customer(**customer) for customer in customers]

@app.post("/customers", response_model=Customer)
async def create_customer(name: str = Form(...), phone: str = Form(...), photo: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    logger.info(f"Creating customer '{name}'")
    
    logger.info("Uploading photo to image service")
    try:
        files = {'photo': (photo.filename, photo.file, photo.content_type)}
        image_response = requests.post(f"{IMAGE_SERVICE_URL}/upload", files=files)
        image_response.raise_for_status()
        photo_url = image_response.json()["url"]
        logger.info("Photo uploaded successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to upload image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to upload image")

    customer_data = {
        "name": name,
        "phone": phone,
        "photo": photo_url
    }
    
    result = customers_collection.insert_one(customer_data)
    created_customer = customers_collection.find_one({"_id": result.inserted_id})
    
    logger.info(f"Customer '{name}' created successfully with ID {result.inserted_id}")
    return Customer(**created_customer)

@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    logger.info(f"Getting customer with ID {customer_id}")
    customer = customers_collection.find_one({"_id": ObjectId(customer_id)})
    if customer is None:
        logger.warning(f"Customer with ID {customer_id} not found")
        raise HTTPException(status_code=404, detail="Customer not found")
    logger.info(f"Customer with ID {customer_id} found")
    return Customer(**customer)

@app.put("/customers/{customer_id}")
async def update_customer(customer_id: str, name: Optional[str] = Form(None), phone: Optional[str] = Form(None), photo: Optional[UploadFile] = File(None), current_user: dict = Depends(get_current_user)):
    logger.info(f"Updating customer with ID {customer_id}")
    update_data = {}
    if name:
        update_data["name"] = name
    if phone:
        update_data["phone"] = phone
    
    if photo:
        logger.info("Uploading photo to image service")
        try:
            files = {'photo': (photo.filename, photo.file, photo.content_type)}
            image_response = requests.post(f"{IMAGE_SERVICE_URL}/upload", files=files)
            image_response.raise_for_status()
            update_data["photo"] = image_response.json()["url"]
            logger.info("Photo uploaded successfully")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload image: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to upload image")

    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    result = customers_collection.update_one({"_id": ObjectId(customer_id)}, {"$set": update_data})
    if result.matched_count == 0:
        logger.warning(f"Customer with ID {customer_id} not found")
        raise HTTPException(status_code=404, detail="Customer not found")

    logger.info(f"Customer with ID {customer_id} updated successfully")
    return {"message": "Customer updated successfully"}

@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    logger.info(f"Deleting customer with ID {customer_id}")
    result = customers_collection.delete_one({"_id": ObjectId(customer_id)})
    if result.deleted_count == 0:
        logger.warning(f"Customer with ID {customer_id} not found")
        raise HTTPException(status_code=404, detail="Customer not found")
    
    logger.info(f"Customer with ID {customer_id} deleted successfully")
    return {"message": "Customer deleted successfully"}

@app.get("/make-me-fail")
async def make_me_fail():
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

@app.get("/i-send-wrong")
async def i_send_wrong():
    return JSONResponse(status_code=400, content={"detail": "Internal Server Error"})

@app.get("/go-sleep")
async def go_sleep():
    a = 1 /0
    return "See me if you can"

@app.get("/health/ready")
async def readiness_probe():
    logger.info("Readiness probe called")
    try:
        # Check DB connection
        client.admin.command('ping')
        logger.info("Database connection is ready")
        
        iam_response = requests.get(f"{IAM_SERVICE_URL}/health/live")
        iam_response.raise_for_status()
        
        image_response = requests.get(f"{IMAGE_SERVICE_URL}/health/live")
        image_response.raise_for_status()

        logger.info("Dependencies are ready")
        return {"status": "Ready"}
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Service not ready: {e}")

@app.get("/health/live")
async def liveness_probe():
    logger.info("Liveness probe called")
    return {"status": "Live"}
