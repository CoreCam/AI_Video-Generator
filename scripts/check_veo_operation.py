"""
Check the status of a VEO 3.1 operation and retrieve the generated video.
"""
import asyncio
import httpx
import os
import json
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def save_video_from_response(response_data: dict) -> bool:
    """Extract video from response and save to file."""
    try:
        # VEO 3.1 response structure uses "videos" key
        videos = response_data.get("videos", [])
        
        if not videos:
            print("❌ No videos in response")
            print(f"Response keys: {list(response_data.keys())}")
            return False
        
        # Get first video
        video_entry = videos[0]
        
        # Get base64 encoded video
        base64_video = video_entry.get("bytesBase64Encoded")
        if not base64_video:
            print("❌ No base64 video data in video entry")
            print(f"Video entry keys: {list(video_entry.keys())}")
            return False
        
        # Decode base64 to binary
        video_bytes = base64.b64decode(base64_video)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"veo_video_{timestamp}.mp4"
        
        # Save to current directory
        with open(filename, 'wb') as f:
            f.write(video_bytes)
        
        file_size_mb = len(video_bytes) / 1024 / 1024
        print(f"\n✅ Video saved: {filename}")
        print(f"   File size: {file_size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving video: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_operation_status(operation_id: str):
    """Check the status of a long-running VEO operation using fetchPredictOperation."""
    
    # Get auth token
    access_token = os.getenv("GOOGLE_ACCESS_TOKEN")
    if not access_token:
        print("❌ GOOGLE_ACCESS_TOKEN not found in environment")
        return
    
    # Get model name from environment or use default
    model_name = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")
    
    # Try both formats: short name and full path
    operation_name = operation_id.split("/operations/")[-1] if "/operations/" in operation_id else operation_id
    full_operation_path = operation_id if operation_id.startswith("projects/") else f"projects/your-project-id/locations/us-central1/publishers/google/models/{model_name}/operations/{operation_id}"
    
    # Use fetchPredictOperation endpoint (VEO-specific)
    fetch_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/your-project-id/locations/us-central1/publishers/google/models/{model_name}:fetchPredictOperation"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    print(f"🔍 Checking VEO operation status...")
    print(f"   Trying full path: {full_operation_path}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Try with full path first
            payload = {"operationName": full_operation_path}
            response = await client.post(fetch_url, headers=headers, json=payload)
            
            # If 404, try with just the short name
            if response.status_code == 404:
                print(f"   Not found with full path, trying short name: {operation_name}")
                payload = {"operationName": operation_name}
                response = await client.post(fetch_url, headers=headers, json=payload)
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if operation is done
                done = result.get("done", False)
                
                if done:
                    print("✅ Operation COMPLETED!")
                    print()
                    
                    # Extract video information
                    if "response" in result:
                        response_data = result["response"]
                        
                        # Save video if it exists
                        video_saved = save_video_from_response(response_data)
                        
                        if not video_saved:
                            # Show full response for debugging
                            print("📹 Full Response:")
                            print(json.dumps(response_data, indent=2))
                        
                        # Look for video URLs
                        predictions = response_data.get("predictions", [])
                        for i, pred in enumerate(predictions):
                            if "generatedSamples" in pred:
                                samples = pred["generatedSamples"]
                                for j, sample in enumerate(samples):
                                    video_uri = sample.get("video", {}).get("uri", "")
                                    if video_uri:
                                        print(f"\n🎬 Video {i+1}.{j+1} URL:")
                                        print(f"   {video_uri}")
                                    
                                    # Also check for gcsUri
                                    gcs_uri = sample.get("video", {}).get("gcsUri", "")
                                    if gcs_uri:
                                        print(f"\n🎬 Video {i+1}.{j+1} GCS URI:")
                                        print(f"   {gcs_uri}")
                    
                    # Check for errors
                    if "error" in result:
                        print("\n❌ Operation completed with error:")
                        print(json.dumps(result["error"], indent=2))
                else:
                    print("⏳ Operation still IN PROGRESS...")
                    
                    # Show metadata if available
                    if "metadata" in result:
                        metadata = result["metadata"]
                        print("\n📊 Progress:")
                        print(json.dumps(metadata, indent=2))
                
                return result
            else:
                print("❌ Error checking operation:")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python check_veo_operation.py <operation_id>")
        print()
        print("Example:")
        print("  python check_veo_operation.py 'projects/your-project-id/locations/us-central1/publishers/google/models/veo-3.1-fast-generate-preview/operations/operation-id-here'")
        sys.exit(1)
    
    operation_id = sys.argv[1]
    asyncio.run(check_operation_status(operation_id))
