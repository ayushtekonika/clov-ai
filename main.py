# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
from fastapi import FastAPI, HTTPException
from fastapi import APIRouter
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from pydantic import BaseModel
from app.optimis import get_summary, extract_entity, icd10
from app.db import db
from app.db.db_calls import add_patient_summary, get_patient_summary

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Optimis instance")
    db.create_connection()
    yield
    print("Closing database connection pool")
    db.close_connection()
    
# Load environment variables
load_dotenv()
app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix="/api/v1")
    
class QueryModel(BaseModel):
    query: str
    patientID: str
    
class entityModel(BaseModel):
    patientID: str

# Define your routes here
@router.get("/health")
async def health():
    return {"status": "ok"}

@router.post("/summary")
async def summary(query_model: QueryModel):
    query = query_model.query
    patientID = query_model.patientID
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' in request body")
    if not patientID:
        raise HTTPException(status_code=400, detail="Missing 'patientID' in request body")

    try:
        response = get_summary(query)
        await add_patient_summary(query_model.patientID, response, db.db_connection)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/get_entity")
async def getEntity(query_model: entityModel):
    patientID = query_model.patientID

    if not patientID:
        raise HTTPException(status_code=400, detail="Missing 'patientID' in request body")

    try:
        
        summary = await get_patient_summary(patientID, db.db_connection)
        response = extract_entity(summary)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/get_icd10")
async def getICD10(query_model: entityModel):
    patientID = query_model.patientID

    if not patientID:
        raise HTTPException(status_code=400, detail="Missing 'patientID' in request body")

    try:
        
        # summary = await get_patient_summary(patientID, db.db_connection)
        summary = """1. i do not feel good. **Chief Complaint:** Paul, a 74-year-old patient, woke up with no mobility in his right shoulder, 
            with no prior injury or specific cause.2. **Symptoms:** Paul experiences stiffness, pain, and limited range of motion 
            in his right shoulder, with pain shooting down to the elbow.3. **Activities:** Paul recently tried throwing a football 
            with his grandson and experienced some soreness, but it was not severe.4. **Sleeping Position:** Paul is a side sleeper 
            and did not notice any unusual sleeping position.5. **Medical History:** Paul has anxiety, depression, and a peanut 
            allergy.6. **Physical Examination:** Paul's shoulder mobility is severely limited, with:* Limited external rotation 
            (20 degrees)* Weak internal rotation (2+)* Limited abduction (75 degrees)* Limited external rotation strength 
            (1)* Limited internal rotation strength.
            """
        response = icd10(summary)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the FastAPI app
app.include_router(router)
# add router prefix api/v1

# to run it locally
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)