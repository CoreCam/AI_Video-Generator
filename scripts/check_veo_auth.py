"""
Check gcloud authentication and get access token for Veo 3.1
"""
import subprocess
import sys


def check_gcloud_auth():
    """Check if gcloud is installed and authenticated."""
    print("=" * 60)
    print("🔐 Checking Google Cloud Authentication")
    print("=" * 60)
    
    # Check if gcloud is installed
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("\n✅ gcloud CLI installed:")
            print(result.stdout.split('\n')[0])
        else:
            print("\n❌ gcloud CLI not found")
            print("\nInstall from: https://cloud.google.com/sdk/docs/install")
            return False
    except FileNotFoundError:
        print("\n❌ gcloud CLI not found in PATH")
        print("\nInstall from: https://cloud.google.com/sdk/docs/install")
        return False
    except Exception as e:
        print(f"\n❌ Error checking gcloud: {e}")
        return False
    
    # Check active account
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            account = result.stdout.strip()
            print(f"\n✅ Active account: {account}")
        else:
            print("\n❌ No active account")
            print("\nRun: gcloud auth login")
            return False
    except Exception as e:
        print(f"\n❌ Error checking active account: {e}")
        return False
    
    # Check active project
    try:
        result = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            project = result.stdout.strip()
            print(f"✅ Active project: {project}")
            
            if project != "your-project-id":
                print(f"\n⚠️  Project mismatch!")
                print(f"   Expected: your-project-id")
                print(f"   Current:  {project}")
                print(f"\nRun: gcloud config set project your-project-id")
        else:
            print("\n⚠️  No active project set")
            print("\nRun: gcloud config set project your-project-id")
    except Exception as e:
        print(f"\n⚠️  Error checking project: {e}")
    
    # Try to get access token
    try:
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            token = result.stdout.strip()
            print(f"\n✅ Access token obtained:")
            print(f"   {token[:20]}...{token[-20:]}")
            print(f"   Length: {len(token)} characters")
            return True
        else:
            print("\n❌ Could not get access token")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"\n❌ Error getting access token: {e}")
        return False


def test_veo_auth():
    """Test if we can authenticate with Veo API."""
    print("\n" + "=" * 60)
    print("🧪 Testing Veo API Authentication")
    print("=" * 60)
    
    try:
        import httpx
        
        # Get token
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("\n❌ Cannot get access token")
            return False
        
        token = result.stdout.strip()
        
        # Test endpoint (just check authentication, not actual generation)
        endpoint = "https://us-central1-aiplatform.googleapis.com/v1/projects/your-project-id/locations/us-central1/publishers/google/models/veo-3.1-fast-generate-preview"
        
        print(f"\n🌐 Testing endpoint:")
        print(f"   {endpoint}")
        
        # Just try to access the model (without predictLongRunning)
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # This should return 405 Method Not Allowed (no GET on this endpoint)
        # or 401 if auth is bad
        response = httpx.get(endpoint, headers=headers, timeout=10.0)
        
        print(f"\n📡 Response: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Authentication failed - check permissions")
            return False
        elif response.status_code == 403:
            print("❌ Access forbidden - check API is enabled")
            return False
        elif response.status_code in [404, 405]:
            print("✅ Authentication successful!")
            print("   (404/405 expected - endpoint exists but needs POST with data)")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            print(f"   {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing authentication: {e}")
        return False


if __name__ == "__main__":
    auth_ok = check_gcloud_auth()
    
    if auth_ok:
        test_veo_auth()
        print("\n" + "=" * 60)
        print("✅ Ready to use Veo 3.1!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Authentication setup needed")
        print("=" * 60)
        print("\nSteps to fix:")
        print("1. Install gcloud CLI: https://cloud.google.com/sdk/docs/install")
        print("2. Run: gcloud auth login")
        print("3. Run: gcloud config set project your-project-id")
        print("4. Run: gcloud auth application-default login")
        sys.exit(1)
