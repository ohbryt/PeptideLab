#!/usr/bin/env python3
"""
Peptide-as-a-Service API Server

FastAPI-based peptide ordering and tracking system.

Usage:
    python3 main.py
    uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import json


# ─── Models ────────────────────────────────────────────────────────────────────

class OrderRequest(BaseModel):
    """Peptide order request."""
    sequence: str = Field(..., description="Amino acid sequence")
    modifications: List[str] = Field(default=[], description="e.g., Ahx, pSer, TFA")
    quantity: str = Field(default="50mg", description="Requested quantity")
    purity: str = Field(default=">95%", description="Required purity")
    assays: List[str] = Field(default=[], description="Additional assays: hplc, ms, spr, cell")
    email: str = Field(..., description="Contact email")
    notes: Optional[str] = Field(None, description="Special instructions")


class OrderResponse(BaseModel):
    """Order response."""
    order_id: str
    sequence: str
    status: str
    created_at: str
    estimated_delivery: str
    price: str
    partner_lab: str
    tracking_url: Optional[str] = None


class OrderStatus(BaseModel):
    """Order status."""
    order_id: str
    status: str
    stage: str
    progress: int
    updated_at: str
    notes: Optional[str] = None


# ─── In-Memory Database ─────────────────────────────────────────────────────────

orders_db = {}


# ─── Pricing Logic ─────────────────────────────────────────────────────────────

def calculate_price(sequence: str, modifications: List[str], assays: List[str], quantity: str) -> dict:
    """Calculate order price."""
    
    # Base price per mg
    base_price_per_mg = 80000
    
    # Length factor
    length = len(sequence.replace("-", "").replace(" ", ""))
    length_factor = max(1, length / 10)
    
    # Modification costs
    mod_costs = {
        "Ahx": 20000,
        "pSer": 30000,
        "TFA": 10000,
        "Acetyl": 15000,
        "Amide": 15000
    }
    mod_cost = sum(mod_costs.get(m, 0) for m in modifications)
    
    # Quantity
    qty_map = {"10mg": 1, "50mg": 4, "100mg": 7, "1g": 50}
    qty_factor = qty_map.get(quantity, 1)
    
    # Assay costs
    assay_costs = {
        "hplc": 50000,
        "ms": 80000,
        "spr": 300000,
        "cell": 500000,
        "admet": 800000
    }
    assay_cost = sum(assay_costs.get(a, 0) for a in assays)
    
    # Calculate total
    synthesis_cost = int((base_price_per_mg * length_factor * qty_factor) + mod_cost)
    total = synthesis_cost + assay_cost
    
    return {
        "synthesis": synthesis_cost,
        "assay": assay_cost,
        "total": total,
        "formatted": f"₩{total:,}"
    }


def assign_partner_lab(modifications: List[str]) -> str:
    """Assign partner lab based on requirements."""
    if "GMP" in modifications or "Pharmaceutical" in modifications:
        return "Peptron (GMP-certified)"
    elif len(modifications) > 2:
        return "Kendrick Labs"
    else:
        return "Anygen"


def calculate_delivery(modifications: List[str], assays: List[str]) -> str:
    """Calculate estimated delivery date."""
    weeks = 3  # base
    
    if modifications:
        weeks += 1
    if assays:
        weeks += 1
    if "spr" in assays or "admet" in assays:
        weeks += 1
    
    delivery = datetime.now() + timedelta(weeks=weeks)
    return delivery.strftime("%Y-%m-%d")


# ─── Order Processing ──────────────────────────────────────────────────────────

def process_order(order_id: str):
    """Background task to process order."""
    import time
    
    stages = [
        ("received", "Order received", 10),
        ("validating", "Validating sequence", 20),
        ("sent_to_lab", "Sent to partner lab", 30),
        ("synthesizing", "Synthesizing peptide", 50),
        ("quality_check", "Quality control", 70),
        ("assaying", "Running assays", 85),
        ("packaging", "Packaging", 95),
        ("shipped", "Shipped to customer", 100)
    ]
    
    for stage, desc, progress in stages:
        time.sleep(2)  # Simulate processing
        orders_db[order_id]["stage"] = desc
        orders_db[order_id]["progress"] = progress
        orders_db[order_id]["updated_at"] = datetime.now().isoformat()
        
        if stage == "shipped":
            orders_db[order_id]["status"] = "completed"
            orders_db[order_id]["tracking_url"] = f"https://tracking.example.com/{order_id}"


# ─── API ────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Peptide-as-a-Service API",
    description="AI-driven peptide synthesis and assay service",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "service": "Peptide-as-a-Service API",
        "version": "0.1.0",
        "status": "operational"
    }


@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(order: OrderRequest, background_tasks: BackgroundTasks):
    """Create a new peptide order."""
    
    # Generate order ID
    order_id = f"PS-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
    
    # Calculate pricing
    pricing = calculate_price(
        order.sequence,
        order.modifications,
        order.assays,
        order.quantity
    )
    
    # Assign partner
    partner = assign_partner_lab(order.modifications)
    
    # Calculate delivery
    delivery = calculate_delivery(order.modifications, order.assays)
    
    # Create order
    order_data = {
        "order_id": order_id,
        "sequence": order.sequence,
        "modifications": order.modifications,
        "quantity": order.quantity,
        "purity": order.purity,
        "assays": order.assays,
        "email": order.email,
        "status": "processing",
        "stage": "Order received",
        "progress": 10,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "estimated_delivery": delivery,
        "price": pricing["formatted"],
        "price_breakdown": pricing,
        "partner_lab": partner,
        "tracking_url": None
    }
    
    orders_db[order_id] = order_data
    
    # Start background processing
    background_tasks.add_task(process_order, order_id)
    
    return OrderResponse(
        order_id=order_id,
        sequence=order.sequence,
        status="processing",
        created_at=order_data["created_at"],
        estimated_delivery=delivery,
        price=pricing["formatted"],
        partner_lab=partner
    )


@app.get("/api/v1/orders/{order_id}", response_model=OrderStatus)
async def get_order_status(order_id: str):
    """Get order status."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    return OrderStatus(
        order_id=order_id,
        status=order["status"],
        stage=order["stage"],
        progress=order["progress"],
        updated_at=order["updated_at"],
        notes=f"Partner: {order['partner_lab']}"
    )


@app.get("/api/v1/orders/{order_id}/results")
async def get_order_results(order_id: str):
    """Get order results (after completion)."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    if order["status"] != "completed":
        return {
            "status": "pending",
            "message": "Order not yet completed",
            "progress": order["progress"]
        }
    
    return {
        "status": "completed",
        "order_id": order_id,
        "sequence": order["sequence"],
        "results": {
            "purity": "98.5% (HPLC)",
            "mass": "Confirmed (MS)",
            "quantity_delivered": order["quantity"],
            "coa": f"/api/v1/orders/{order_id}/coa"
        }
    }


@app.get("/api/v1/pricing")
async def get_pricing():
    """Get pricing information."""
    return {
        "synthesis": {
            "base_per_mg": "₩80,000",
            "per_10_residues": "₩80,000",
            "modified_residue": "₩15,000-30,000"
        },
        "assays": {
            "hplc": "₩50,000",
            "ms": "₩80,000",
            "spr": "₩300,000",
            "cell": "₩500,000",
            "admet": "₩800,000"
        },
        "packages": {
            "basic": "₩250,000 (synthesis + HPLC)",
            "standard": "₩400,000 (synthesis + HPLC + MS)",
            "premium": "₩1,200,000 (synthesis + full assays)"
        }
    }


@app.get("/api/v1/partners")
async def get_partners():
    """Get partner labs."""
    return {
        "synthesis": [
            {"name": "Anygen", "min_qty": "10mg", "lead_time": "2-3 weeks", "notes": "Standard"},
            {"name": "Kendrick Labs", "min_qty": "10mg", "lead_time": "2 weeks", "notes": "High purity"},
            {"name": "Peptron", "min_qty": "50mg", "lead_time": "3-4 weeks", "notes": "GMP certified"}
        ],
        "assay": [
            {"name": "KIST", "services": ["SPR", "BLI"], "lead_time": "2 weeks"},
            {"name": "SNU", "services": ["Cell-based", "Binding"], "lead_time": "3 weeks"},
            {"name": "Korea University", "services": ["ADMET"], "lead_time": "4 weeks"}
        ]
    }


# ─── Run Server ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
