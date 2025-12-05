"""
Simple launcher for CINEGEN Chat UI
Run this to start the Streamlit interface
"""
import subprocess
import sys
import os

def main():
    """Launch the CINEGEN chat UI."""
    print("🎬 Starting CINEGEN Chat UI...")
    print("📝 Make sure you have set your GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable")
    print("🌐 The UI will open in your default browser")
    print()
    
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "cinegen_chat_ui.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 CINEGEN Chat UI stopped")
    except Exception as e:
        print(f"❌ Error starting UI: {e}")
        print("💡 Make sure streamlit is installed: pip install streamlit")

if __name__ == "__main__":
    main()