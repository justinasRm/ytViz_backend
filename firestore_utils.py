from firestore_client import get_firestore_client
from google.cloud import firestore
from datetime import datetime

db = get_firestore_client()

def getAPIQuota():
    '''
    Get API quota from Firestore.
    '''
    currentDay = f'{datetime.now().year}-{datetime.now().month}-{datetime.now().day}'

    doc_ref = db.collection('APIQuota').document(currentDay)

    if not doc_ref.get().exists:
        doc_ref.set({
            'quotaUsed': 0
        })
        return 0
    else:
        return doc_ref.get().to_dict()['quotaUsed']


def updateAPIQuota(add: int):
    '''
    Update API quota in Firestore.
    '''
    currentDay = f'{datetime.now().year}-{datetime.now().month}-{datetime.now().day}'
    
    doc_ref = db.collection('APIQuota').document(currentDay)
    doc_snapshot = doc_ref.get()

    if doc_snapshot.exists:
        doc_ref.update({
            'quotaUsed': firestore.Increment(add)
        })
    else:
        doc_ref.set({
            'quotaUsed': add
        })

    return {"message": "Data updated successfully."}

def setAPIQuotaMAX():
    currentDay = f'{datetime.now().year}-{datetime.now().month}-{datetime.now().day}'
    
    doc_ref = db.collection('APIQuota').document(currentDay)
    doc_snapshot = doc_ref.get()

    if doc_snapshot.exists:
        doc_ref.update({
            'quotaUsed': 10000
        })
    else:
        doc_ref.set({
            'quotaUsed': 10000
        })

    return {"message": "Data updated successfully."}