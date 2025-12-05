"""
Extract reference frames from persona videos for VEO subject consistency.
These frames will be used as visual references so VEO knows what the person looks like.
"""
import cv2
import os
from pathlib import Path
import json


def extract_reference_frames(video_path: str, output_dir: str, num_frames: int = 5):
    """
    Extract evenly-spaced frames from a video as reference images.
    
    Args:
        video_path: Path to input video
        output_dir: Directory to save frames
        num_frames: Number of frames to extract
    """
    video_name = Path(video_path).stem
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return []
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"📹 {video_name}: {total_frames} frames, {duration:.1f}s")
    
    # Calculate frame indices to extract (evenly spaced)
    frame_indices = [int(i * total_frames / (num_frames + 1)) for i in range(1, num_frames + 1)]
    
    extracted_frames = []
    
    for idx, frame_num in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        
        if ret:
            frame_filename = f"{video_name}_frame_{idx+1}.jpg"
            frame_path = output_path / frame_filename
            cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            extracted_frames.append(str(frame_path))
            print(f"   ✅ Extracted frame {idx+1}/{num_frames}: {frame_filename}")
        else:
            print(f"   ❌ Failed to extract frame {frame_num}")
    
    cap.release()
    return extracted_frames


def process_persona_videos(persona_dir: str = "personas/example_persona"):
    """Process all videos in a persona directory."""
    
    persona_path = Path(persona_dir)
    videos_path = persona_path / "videos"
    reference_frames_path = persona_path / "reference_frames"
    
    if not videos_path.exists():
        print(f"❌ Videos directory not found: {videos_path}")
        return
    
    print("=" * 60)
    print("🎬 Extracting Reference Frames for VEO")
    print("=" * 60)
    print(f"\nSource: {videos_path}")
    print(f"Output: {reference_frames_path}\n")
    
    # Process each video
    video_files = list(videos_path.glob("*.mp4"))
    
    if not video_files:
        print("❌ No .mp4 files found in videos directory")
        return
    
    all_frames = {}
    
    for video_file in video_files:
        emotion = video_file.stem.replace(f"{Path(persona_dir).name}_", "")
        print(f"\n📹 Processing: {video_file.name} ({emotion})")
        
        frames = extract_reference_frames(
            str(video_file),
            str(reference_frames_path / emotion),
            num_frames=3  # 3 frames per emotion video
        )
        
        all_frames[emotion] = frames
    
    # Save reference manifest
    manifest = {
        "persona_id": "example_001",
        "name": "ExamplePersona",
        "reference_frames": all_frames,
        "total_frames": sum(len(frames) for frames in all_frames.values()),
        "emotions": list(all_frames.keys()),
        "usage": "These frames serve as visual references for VEO to maintain subject consistency"
    }
    
    manifest_path = reference_frames_path / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("\n" + "=" * 60)
    print("✅ Reference Frame Extraction Complete!")
    print("=" * 60)
    print(f"Total frames: {manifest['total_frames']}")
    print(f"Emotions covered: {', '.join(manifest['emotions'])}")
    print(f"Manifest: {manifest_path}")
    print("\n💡 These frames will be used by VEO for subject consistency")


if __name__ == "__main__":
    try:
        import cv2
        process_persona_videos()
    except ImportError:
        print("❌ opencv-python not installed")
        print("Install with: pip install opencv-python")
