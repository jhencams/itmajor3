from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

app = FastAPI()


medicines_db = []
users_db = []


class Medicine(BaseModel):
    id: int
    name: str
    dosage: str
    frequency: int  
    start_date: datetime
    end_date: Optional[datetime]
    notes: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    email: str
    medicines: List[Medicine] = []

class MedicineUpdate(BaseModel):
    dosage: Optional[str]
    frequency: Optional[int]
    end_date: Optional[datetime]
    notes: Optional[str]


@app.post("/users/")
def create_user(user: User):
    users_db.append(user)
    return {"msg": "User created successfully", "user": user}


@app.get("/users/", response_model=List[User])
def get_users():
    return users_db


@app.post("/users/{user_id}/medicines/")
def add_medicine(user_id: int, medicine: Medicine):
    for user in users_db:
        if user.id == user_id:
            user.medicines.append(medicine)
            return {"msg": "Medicine added successfully", "medicine": medicine}
    raise HTTPException(status_code=404, detail="User not found")


@app.get("/users/{user_id}/medicines/", response_model=List[Medicine])
def get_user_medicines(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user.medicines
    raise HTTPException(status_code=404, detail="User not found")


@app.put("/users/{user_id}/medicines/{medicine_id}")
def update_medicine(user_id: int, medicine_id: int, medicine_update: MedicineUpdate):
    for user in users_db:
        if user.id == user_id:
            for med in user.medicines:
                if med.id == medicine_id:
                    if medicine_update.dosage:
                        med.dosage = medicine_update.dosage
                    if medicine_update.frequency:
                        med.frequency = medicine_update.frequency
                    if medicine_update.end_date:
                        med.end_date = medicine_update.end_date
                    if medicine_update.notes:
                        med.notes = medicine_update.notes
                    return {"msg": "Medicine updated successfully", "medicine": med}
    raise HTTPException(status_code=404, detail="Medicine/User not found")


@app.delete("/users/{user_id}/medicines/{medicine_id}")
def delete_medicine(user_id: int, medicine_id: int):
    for user in users_db:
        if user.id == user_id:
            user.medicines = [med for med in user.medicines if med.id != medicine_id]
            return {"msg": "Medicine deleted successfully"}
    raise HTTPException(status_code=404, detail="User/Medicine not found")


@app.get("/users/{user_id}/medicines/{medicine_id}", response_model=Medicine)
def get_medicine_by_id(user_id: int, medicine_id: int):
    for user in users_db:
        if user.id == user_id:
            for med in user.medicines:
                if med.id == medicine_id:
                    return med
    raise HTTPException(status_code=404, detail="Medicine/User not found")


class ConsumptionRecord(BaseModel):
    time_taken: datetime
    notes: Optional[str] = None

consumption_db = []

@app.post("/users/{user_id}/medicines/{medicine_id}/track")
def track_medicine(user_id: int, medicine_id: int, consumption: ConsumptionRecord):
    for user in users_db:
        if user.id == user_id:
            for med in user.medicines:
                if med.id == medicine_id:
                    consumption_db.append({
                        "user_id": user_id,
                        "medicine_id": medicine_id,
                        "time_taken": consumption.time_taken,
                        "notes": consumption.notes
                    })
                    return {"msg": "Consumption tracked successfully", "record": consumption}
    raise HTTPException(status_code=404, detail="Medicine/User not found")


@app.get("/users/{user_id}/medicines/{medicine_id}/track", response_model=List[ConsumptionRecord])
def get_consumption_records(user_id: int, medicine_id: int):
    records = [record for record in consumption_db if record['user_id'] == user_id and record['medicine_id'] == medicine_id]
    return records


@app.post("/users/{user_id}/medicines/{medicine_id}/reminder")
def set_reminder(user_id: int, medicine_id: int, hours_before: int):
    reminder_time = datetime.now() + timedelta(hours=hours_before)
    return {"msg": f"Reminder set for {reminder_time}"}

@app.get("/users/{user_id}/reminders/")
def get_reminders(user_id: int):
    return {"msg": "List of reminders", "reminders": []}

@app.get("/users/{user_id}/medicines/search/")
def search_medicine(user_id: int, query: str):
    for user in users_db:
        if user.id == user_id:
            filtered_medicines = [med for med in user.medicines if query.lower() in med.name.lower()]
            return {"msg": "Search results", "medicines": filtered_medicines}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/{user_id}/medicines/expiring/")
def get_expiring_medicines(user_id: int, days: int = 7):
    for user in users_db:
        if user.id == user_id:
            expiring_meds = [med for med in user.medicines if med.end_date and (med.end_date - datetime.now()).days <= days]
            return {"msg": "Expiring medicines", "medicines": expiring_meds}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users/{user_id}/medicines/{medicine_id}/refill-reminder")
def set_refill_reminder(user_id: int, medicine_id: int, days_before: int):
    refill_time = datetime.now() + timedelta(days=days_before)
    return {"msg": f"Refill reminder set for {refill_time}"}

@app.get("/users/refill-reminders/")
def get_refill_reminders():
    return {"msg": "List of users who need refills", "users": []}

class MissedDose(BaseModel):
    time_missed: datetime
    reason: Optional[str]

missed_doses_db = []

@app.post("/users/{user_id}/medicines/{medicine_id}/missed-dose")
def record_missed_dose(user_id: int, medicine_id: int, missed_dose: MissedDose):
    missed_doses_db.append({
        "user_id": user_id,
        "medicine_id": medicine_id,
        "time_missed": missed_dose.time_missed,
        "reason": missed_dose.reason
    })
    return {"msg": "Missed dose recorded successfully"}

@app.get("/users/{user_id}/missed-doses/")
def get_missed_doses(user_id: int):
    missed_doses = [dose for dose in missed_doses_db if dose["user_id"] == user_id]
    return {"msg": "Missed doses", "missed_doses": missed_doses}

@app.get("/users/{user_id}/adherence/")
def get_adherence_rate(user_id: int):
    total_medicines = sum(len(user.medicines) for user in users_db if user.id == user_id)
    total_tracked = len([record for record in consumption_db if record['user_id'] == user_id])
    adherence_rate = (total_tracked / total_medicines) * 100 if total_medicines > 0 else 0
    return {"msg": f"User adherence rate: {adherence_rate}%"}

@app.get("/users/{user_id}/medicines/overdue/")
def get_overdue_medicines(user_id: int):
    overdue_meds = [med for med in users_db if med["user_id"] == user_id and med["time_taken"] < datetime.now()]
    return {"msg": "Overdue medicines", "medicines": overdue_meds}

@app.get("/users/{user_id}/medicines/today/")
def get_today_medicine_reminders(user_id: int):
    today_meds = [med for med in consumption_db if med['user_id'] == user_id and med['time_taken'].date() == datetime.now().date()]
    return {"msg": "Medicines for today", "medicines": today_meds}
