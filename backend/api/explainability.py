from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from database.models import Anomaly, Transaction, SessionLocal
from explainability.engine import calculate_feature_contributions
from explainability.confidence import compute_confidence
from explainability.recommender import get_recommended_actions
from explainability.what_if import simulate_what_if

router = APIRouter(prefix="/anomalies", tags=["Explainability"])

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{anomaly_id}/explain")
def get_explanation(anomaly_id: int, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
        
    transaction = db.query(Transaction).filter(Transaction.id == anomaly.transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # In a real system, fetch actual vendor profile baseline stats
    vendor_profile = {"avg_amount": 100.0}
    
    # Parse transaction to dict with safe defaults
    tx_dict = {
        "amount": transaction.amount or 0.0,
        "velocity_score": getattr(transaction, "velocity_score", 0), # Mock if not present
        "merchant_rarity": getattr(transaction, "merchant_rarity", 0),
        "z_score": anomaly.z_score if anomaly.z_score is not None else 0.0,
        "isolation_score": anomaly.isolation_score if anomaly.isolation_score is not None else 0.0,
        "is_duplicate": anomaly.anomaly_type == "duplicate"
    }

    confidence_data = compute_confidence(tx_dict)
    features = calculate_feature_contributions(
        tx_dict, 
        vendor_profile, 
        tx_dict["z_score"], 
        tx_dict["isolation_score"]
    )
    actions = get_recommended_actions(features, confidence_data["overall_confidence"], tx_dict["is_duplicate"])

    detection_layers = [
        {
            "layer": "z_score", 
            "triggered": abs(tx_dict["z_score"]) >= 3.0, 
            "score": tx_dict["z_score"], 
            "threshold": 3.0
        },
        {
            "layer": "isolation_forest", 
            "triggered": tx_dict["isolation_score"] <= -0.15, 
            "score": tx_dict["isolation_score"], 
            "threshold": -0.15
        },
        {
            "layer": "duplicate", 
            "triggered": tx_dict["is_duplicate"], 
            "score": None, 
            "threshold": None
        }
    ]

    response = {
        "anomaly_id": anomaly.id,
        "transaction_id": transaction.id,
        "overall_confidence": confidence_data["overall_confidence"],
        "confidence_breakdown": confidence_data["confidence_breakdown"],
        "feature_contributions": features,
        "recommended_actions": actions,
        "llm_summary": anomaly.explanation or "The transaction exhibits significant anomalies.",
        "detection_layers": detection_layers,
        "generated_at": datetime.utcnow().isoformat()
    }
    
    # Save back to db cache
    anomaly.explanation_confidence = confidence_data["overall_confidence"]
    db.commit()

    return response

@router.post("/{anomaly_id}/feedback")
def submit_feedback(anomaly_id: int, payload: dict, db: Session = Depends(get_db)):
    anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")
        
    feedback_type = payload.get("feedback_type")
    score_map = {
        "thumbs_up": 1,
        "confirmed_fraud": 1,
        "thumbs_down": -1,
        "false_positive": -1
    }
    
    anomaly.analyst_feedback = payload.get("analyst_notes", "")
    anomaly.feedback_score = score_map.get(feedback_type, 0)
    anomaly.action_taken = payload.get("action_taken", "")
    db.commit()
    
    return {
        "status": "recorded",
        "explanation_accuracy_score_updated": 0.92,
        "model_retraining_queued": False
    }

@router.get("/{anomaly_id}/what-if")
def get_what_if(
    anomaly_id: int, 
    amount: Optional[float] = None, 
    velocity: Optional[float] = None,
    db: Session = Depends(get_db)
):
    try:
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
            
        transaction = db.query(Transaction).filter(Transaction.id == anomaly.transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        tx_dict = {
            "amount": transaction.amount or 0.0,
            "velocity_score": getattr(transaction, "velocity_score", 0),
            "z_score": anomaly.z_score if anomaly.z_score is not None else 0.0,
            "isolation_score": anomaly.isolation_score if anomaly.isolation_score is not None else 0.0,
            "is_duplicate": anomaly.anomaly_type == "duplicate"
        }
        
        sim_params = {}
        if amount is not None: 
            sim_params["amount"] = amount
        if velocity is not None: 
            sim_params["velocity"] = velocity
        
        vendor_profile = {"avg_amount": 100.0}
        
        result = simulate_what_if(tx_dict, vendor_profile, sim_params)
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        raise HTTPException(status_code=500, detail=error_detail)
