import pymongo

def add(db, data):
    db.insert_one(data)

def find(db, data, filter):
    return list(db.find(data, filter))

def findOne(db, data, filter):
    return db.find_one(data,filter)

def update(db,data, newData):
    db.update_one(data,newData)