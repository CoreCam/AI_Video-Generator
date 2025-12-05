"""
Direct Prompt to Video Generator
Simply pass your prompt and generate a video with your persona!
"""
import asyncio
import sys
from dotenv import load_dotenv
from video_clients.unified_client import UnifiedVideoClient

# Load environment variables
load_dotenv()

async def generate_video_from_prompt(prompt: str, duration: int = 8):
    """
    Generate a video directly from a text prompt.
    
    Personas are automatically detected from the prompt text.
    - If you mention a persona name (e.g., "John"), it will be included
    - If you don't mention any persona, a generic video is generated
    
    Args:
        prompt: Your video description
        duration: Video length in seconds (default 8)
    """
    
    print(f"\n🎬 DIRECT PROMPT TO VIDEO")
    print(f"{'=' * 70}\n")
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️  Duration: {duration}s")
    print(f"🤖 Personas: Auto-detected from prompt")
    print(f"\n{'=' * 70}\n")
    
    # Initialize client
    client = UnifiedVideoClient()
    
    # Create script
    script = {
        'prompt': prompt,
        'duration': duration
    }
    
    # Generate video - personas will be auto-detected
    print("🚀 Generating video...\n")
    result = await client.generate_video(
        script, 
        provider='velo'
    )
    
    if result.get('success'):
        operation_id = result.get('operation_id')
        if operation_id:
            # Extract just the operation ID part
            if '/' in operation_id:
                short_id = operation_id.split('/')[-1]
            else:
                short_id = operation_id
            
            print(f"\n{'=' * 70}")
            print(f"✅ VIDEO GENERATION STARTED!")
            print(f"{'=' * 70}\n")
            print(f"🎥 Operation ID: {short_id}")
            print(f"📊 Status: {result.get('status')}")
            print(f"\n💡 Check status with:")
            print(f"   python scripts/check_veo_operation.py \"{short_id}\"\n")
            print(f"⏰ Videos usually take 2-3 minutes to generate")
            print(f"{'=' * 70}\n")
        else:
            print(f"\n⚠️ Result: {result}")
    else:
        print(f"\n❌ Generation failed: {result.get('message', 'Unknown error')}")
    
    return result


def main():
    """Main entry point."""
    
    # Check if prompt provided as argument
    if len(sys.argv) > 1:
        # Use command line argument
        prompt = ' '.join(sys.argv[1:])
    else:
        # Interactive mode
        print("\n🎬 DIRECT PROMPT TO VIDEO GENERATOR")
        print("=" * 70)
        print("Enter your video prompt (or press Enter for example):")
        print()
        
        prompt = input("Prompt: ").strip()
        
        if not prompt:
            # Default example
            prompt = "John sitting at a modern desk, focused and inspired, working on his laptop with a smile"
            print(f"\nUsing example: {prompt}\n")
    
    # Generate video
    result = asyncio.run(generate_video_from_prompt(prompt))
    
    return result


if __name__ == "__main__":
    main()
