"""
Decode and save the VEO generated video from the operation response.
"""
import base64
import sys
import json

def save_video(base64_video_data: str, output_path: str = "generated_video.mp4"):
    """Decode base64 video and save to file."""
    try:
        # Decode base64 to binary
        video_bytes = base64.b64decode(base64_video_data)
        
        # Save to file
        with open(output_path, 'wb') as f:
            f.write(video_bytes)
        
        print(f"✅ Video saved successfully: {output_path}")
        print(f"   File size: {len(video_bytes) / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"❌ Error saving video: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python save_veo_video.py <base64_video_data> [output_path]")
        print()
        print("The base64 data should be from the VEO operation response.")
        sys.exit(1)
    
    video_data = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "generated_video.mp4"
    
    save_video(video_data, output_path)
