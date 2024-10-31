from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Medicine Model
class Medicine(BaseModel):
    id: int
    name: str
    dosage: str
    frequency: int  # times per day
    start_date: datetime
    end_date: Optional[datetime]
    notes: Optional[str] = None

# User Model
class User(BaseModel):
    id: int
    name: str
    email: str
    medicines: List[Medicine] = []

# Medicine Update Model
class MedicineUpdate(BaseModel):
    dosage: Optional[str]
    frequency: Optional[int]
    end_date: Optional[datetime]
    notes: Optional[str]

# Consumption Record Model
class ConsumptionRecord(BaseModel):
    time_taken: datetime
    notes: Optional[str] = None

# Missed Dose Model
class MissedDose(BaseModel):
    time_missed: datetime
    reason: Optional[str]
