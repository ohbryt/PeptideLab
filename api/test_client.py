#!/usr/bin/env python3
"""
Peptide-as-a-Service Test Client

Usage:
    python3 test_client.py
"""

import requests
import json
import time


BASE_URL = "http://localhost:8000"


def test_api():
    """Test all API endpoints."""
    
    print("="*50)
    print(" Peptide-as-a-Service API Test")
    print("="*50)
    
    # 1. Root
    print("\n1. Testing root endpoint...")
    r = requests.get(f"{BASE_URL}/")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")
    
    # 2. Pricing
    print("\n2. Testing pricing endpoint...")
    r = requests.get(f"{BASE_URL}/api/v1/pricing")
    print(f"   Status: {r.status_code}")
    print(f"   Price (Standard): {r.json()['packages']['standard']}")
    
    # 3. Partners
    print("\n3. Testing partners endpoint...")
    r = requests.get(f"{BASE_URL}/api/v1/partners")
    print(f"   Status: {r.status_code}")
    partners = r.json()['synthesis']
    print(f"   Synthesis partners: {[p['name'] for p in partners]}")
    
    # 4. Create Order
    print("\n4. Creating test order...")
    order_data = {
        "sequence": "YGRKKRRQRRR-Ahx-DFTFVSNPKUWNNAV-GG-pSer-Y",
        "modifications": ["Ahx", "pSer"],
        "quantity": "50mg",
        "purity": ">95%",
        "assays": ["hplc", "ms"],
        "email": "test@research.kr",
        "notes": "GPX4-MIM-004 peptide"
    }
    
    r = requests.post(f"{BASE_URL}/api/v1/orders", json=order_data)
    print(f"   Status: {r.status_code}")
    
    if r.status_code == 200:
        order = r.json()
        print(f"   Order ID: {order['order_id']}")
        print(f"   Price: {order['price']}")
        print(f"   Partner: {order['partner_lab']}")
        print(f"   Delivery: {order['estimated_delivery']}")
        
        order_id = order['order_id']
        
        # 5. Check Status
        print(f"\n5. Checking order status ({order_id})...")
        for i in range(3):
            r = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}")
            status = r.json()
            print(f"   [{i+1}] Status: {status['status']} | Progress: {status['progress']}% | {status['stage']}")
            if status['status'] == 'completed':
                break
            time.sleep(3)
        
        # 6. Get Results
        print(f"\n6. Getting order results...")
        r = requests.get(f"{BASE_URL}/api/v1/orders/{order_id}/results")
        result = r.json()
        print(f"   Status: {result['status']}")
        if result['status'] == 'completed':
            print(f"   Purity: {result['results']['purity']}")
    
    print("\n" + "="*50)
    print(" Test Complete!")
    print("="*50)


if __name__ == "__main__":
    test_api()
