from firestore_client import get_firestore_client
from google.cloud import firestore
db = get_firestore_client()

def getAPIQuota():
    '''
    Get API quota from Firestore.
    '''
    doc_ref = db.collection('APIQuota').document('APIQuota')
    doc = doc_ref.get().to_dict()
    return doc['currNum']

def updateAPIQuota(add: int):
    '''
    Update API quota in Firestore.
    '''
    doc_ref = db.collection('APIQuota').document('APIQuota')
    doc_ref.set({
        'currNum': firestore.Increment(add)
    }, merge=True)
    return {"message": "Data updated successfully."}