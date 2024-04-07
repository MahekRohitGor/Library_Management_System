from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from bson.json_util import dumps
from typing import Optional

# Initialize FastAPI app
app = FastAPI()

# Initialize MongoDB client
client = MongoClient("mongodb+srv://1mahekgor1:zxb5lM3GOkEt8s1Y@cluster0.3urrgff.mongodb.net/lib_management_data?retryWrites=true&w=majority")
db = client["lib_management_data"]

# Define Pydantic models for data validation
class AddressPatch(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None

class StudentPatch(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[AddressPatch] = None
class Address(BaseModel):
    city: str
    country: str
class Student(BaseModel):
    name: str
    age: int
    address: Address

# API endpoint to create a new student
@app.post("/students/")
async def create_student(student: Student):
    result = db.students.insert_one(student.dict())
    return {"id": str(result.inserted_id)}

# API endpoint to read a student by ID
@app.get("/students/{id}")
async def read_student(id: str):
    student_obj_id = ObjectId(id)
    student = db.students.find_one({"_id": student_obj_id})
    
    if student:
        # Convert ObjectId to string for JSON serialization
        student["_id"] = str(student["_id"])
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# API endpoint to update a student by ID
@app.patch("/students/{id}")
async def update_student(id: str, student_patch: StudentPatch):
    student_obj_id = ObjectId(id)
    update_fields = student_patch.dict(exclude_unset=True)  # Exclude fields with None values
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    result = db.students.update_one({"_id": student_obj_id}, {"$set": update_fields})
    if result.modified_count == 1:
        return
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# API endpoint to delete a student by ID
@app.delete("/students/{id}")
async def delete_student(id: str):
    student_obj_id = ObjectId(id)
    result = db.students.delete_one({"_id": student_obj_id})
    if result.deleted_count == 1:
        return
    else:
        raise HTTPException(status_code=404, detail="Student not found")

# API endpoint to get all students with optional filters
@app.get("/students/")
async def get_all_students(country: str = Query(None), age: int = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    
    students = db.students.find(query)
    students = [student for student in students]
    for student in students:
        student["_id"] = str(student["_id"]) # Convert ObjectId to string for JSON serialization
    return {"data": students}