#!/usr/bin/env python3
"""
API Performance Testing Script
Tests deployed backend speed and response times
"""

import time
import requests
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict

BASE_URL = "https://trading-bot-api-7xps.onrender.com"

# Test credentials (public test user)
TEST_EMAIL = "admin@example.com"
TEST_PASSWORD = "admin123"

def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def test_endpoint(url: str, method: str = "GET", json_data: dict = None, headers: dict = None) -> Dict:
    """Test a single endpoint and return performance metrics"""
    start = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=json_data, headers=headers, timeout=30)
        else:
            response = requests.request(method, url, json=json_data, headers=headers, timeout=30)
        
        duration = time.time() - start
        
        return {
            "success": True,
            "status": response.status_code,
            "duration": duration,
            "size": len(response.content),
            "error": None
        }
    except Exception as e:
        duration = time.time() - start
        return {
            "success": False,
            "status": 0,
            "duration": duration,
            "size": 0,
            "error": str(e)
        }

def print_result(name: str, result: Dict):
    """Print test result"""
    if result["success"]:
        status_icon = "✅" if result["status"] < 400 else "❌"
        print(f"{status_icon} {name:30} | {result['duration']:.3f}s | HTTP {result['status']} | {result['size']:,} bytes")
    else:
        print(f"❌ {name:30} | {result['duration']:.3f}s | ERROR: {result['error'][:40]}")

def main():
    print_header("🚀 BACKEND API PERFORMANCE TEST")
    
    # 1. Test Basic Endpoints
    print_header("📡 Testing Basic Endpoints (No Auth)")
    
    endpoints = [
        ("Root Endpoint", f"{BASE_URL}/"),
        ("API Info", f"{BASE_URL}/api"),
        ("API Docs", f"{BASE_URL}/docs"),
        ("OpenAPI Spec", f"{BASE_URL}/openapi.json"),
    ]
    
    basic_times = []
    for name, url in endpoints:
        result = test_endpoint(url)
        print_result(name, result)
        if result["success"]:
            basic_times.append(result["duration"])
    
    # 2. Test Authentication
    print_header("🔐 Testing Authentication")
    
    # Login
    login_result = test_endpoint(
        f"{BASE_URL}/api/auth/login",
        method="POST",
        json_data={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    print_result("Login", login_result)
    
    # Get token if login successful
    token = None
    if login_result["success"] and login_result["status"] == 200:
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                print(f"🔑 Token obtained: {token[:20]}..." if token else "⚠️ No token in response")
        except Exception as e:
            print(f"⚠️ Could not extract token: {e}")
    
    # 3. Test Protected Endpoints
    if token:
        print_header("🛡️ Testing Protected Endpoints (With Auth)")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        protected_endpoints = [
            ("Get Profile", f"{BASE_URL}/api/auth/me"),
            ("Get Dashboard", f"{BASE_URL}/api/dashboard"),
            ("Get Balance", f"{BASE_URL}/api/user/balance"),
            ("Admin Bot Status", f"{BASE_URL}/api/new-listing/status"),
        ]
        
        protected_times = []
        for name, url in protected_endpoints:
            result = test_endpoint(url, headers=headers)
            print_result(name, result)
            if result["success"]:
                protected_times.append(result["duration"])
    else:
        print("⚠️ Skipping protected endpoints (no token)")
        protected_times = []
    
    # 4. Test Concurrent Requests
    print_header("⚡ Testing Concurrent Performance")
    
    def concurrent_test(num_requests: int):
        """Test multiple concurrent requests"""
        start = time.time()
        
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [
                executor.submit(test_endpoint, f"{BASE_URL}/api")
                for _ in range(num_requests)
            ]
            results = [f.result() for f in futures]
        
        duration = time.time() - start
        successful = sum(1 for r in results if r["success"])
        avg_time = statistics.mean([r["duration"] for r in results if r["success"]])
        
        return {
            "total_time": duration,
            "successful": successful,
            "failed": num_requests - successful,
            "avg_response": avg_time
        }
    
    # Test different concurrency levels
    for num in [5, 10]:
        result = concurrent_test(num)
        print(f"📊 {num} concurrent requests:")
        print(f"   Total Time: {result['total_time']:.3f}s")
        print(f"   Successful: {result['successful']}/{num}")
        print(f"   Avg Response: {result['avg_response']:.3f}s")
        print(f"   Requests/sec: {num/result['total_time']:.2f}")
        print()
    
    # 5. Summary
    print_header("📊 PERFORMANCE SUMMARY")
    
    all_times = basic_times + protected_times
    if all_times:
        print(f"✅ Fastest Response:  {min(all_times):.3f}s")
        print(f"⏱️  Average Response:  {statistics.mean(all_times):.3f}s")
        print(f"⚠️  Slowest Response:  {max(all_times):.3f}s")
        print(f"📈 Median Response:   {statistics.median(all_times):.3f}s")
        
        # Speed rating
        avg = statistics.mean(all_times)
        if avg < 0.5:
            rating = "🚀 EXCELLENT (< 0.5s)"
        elif avg < 1.0:
            rating = "✅ GOOD (< 1.0s)"
        elif avg < 2.0:
            rating = "⚠️  ACCEPTABLE (< 2.0s)"
        else:
            rating = "❌ SLOW (> 2.0s)"
        
        print(f"\n🎯 Overall Speed: {rating}")
    
    # 6. Recommendations
    print_header("💡 RECOMMENDATIONS")
    
    avg_time = statistics.mean(all_times) if all_times else 0
    
    if avg_time < 0.5:
        print("✅ Backend is VERY FAST!")
        print("   - Upgraded instance is working perfectly")
        print("   - No optimizations needed")
    elif avg_time < 1.0:
        print("✅ Backend is performing well")
        print("   - Speed is good for mobile app")
        print("   - Consider caching for further optimization")
    elif avg_time < 2.0:
        print("⚠️  Backend could be faster")
        print("   - Consider adding Redis caching")
        print("   - Check database query optimization")
    else:
        print("❌ Backend needs optimization")
        print("   - Add database indexes")
        print("   - Implement caching layer")
        print("   - Check for slow queries")
    
    print("\n" + "=" * 60)
    print("✅ Performance test complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
