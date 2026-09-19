from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db
from auth import get_current_user

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

@router.get("", response_model=List[schemas.Invoice])
def read_invoices(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Correctly scoped to current user
    return db.query(models.Invoice).filter(models.Invoice.owner_id == current_user.id).all()

@router.get("/{invoice_id}", response_model=schemas.Invoice)
def read_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # VULNERABILITY: BOLA / IDOR. Missing check if invoice belongs to current_user
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice
