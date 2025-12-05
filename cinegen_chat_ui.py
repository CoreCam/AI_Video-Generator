"""
Simple Streamlit Chat UI for CINEGEN Story Director
Clean interface for interactive storytelling without touching core system.
"""
import streamlit as st
import asyncio
import json
import os
from typing import Dict, Any

# Import your existing CINEGEN system
from storytelling.enhanced_cinegen import EnhancedCinegenAgent
from storage.vector_store import VectorStore
from storage.db import DatabaseClient


class CinegenChatUI:
    """Simple chat interface for CINEGEN."""
    
    def __init__(self):
        self.cinegen = None
        self.current_session_id = None
        
    async def initialize_cinegen(self):
        """Initialize the CINEGEN agent."""
        if self.cinegen is None:
            # Use your existing components
            vector_store = VectorStore()
            db_client = DatabaseClient()
            
            self.cinegen = EnhancedCinegenAgent(
                vector_store=vector_store,
                db_client=db_client,
                # Prefer GEMINI_API_KEY, fallback to GOOGLE_API_KEY
                google_api_key=(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")),
                temperature=0.9
            )
        return self.cinegen
    
    async def start_new_session(self, persona_ids=None, target_duration=60):
        """Start a new CINEGEN story session."""
        cinegen = await self.initialize_cinegen()
        
        self.current_session_id = await cinegen.start_story_session(
            persona_ids=persona_ids or [],  # No default personas - will be detected dynamically
            target_duration=target_duration
        )
        return self.current_session_id
    
    async def process_prompt(self, user_prompt: str, duration_seconds: int = 30):
        """Process user prompt directly through CINEGEN - let Gemini handle the natural language."""
        if not self.cinegen or not self.current_session_id:
            await self.start_new_session()
        
        # Send user input directly to CINEGEN - no preprocessing needed
        breakdown = await self.cinegen.process_user_prompt(
            user_prompt, 
            duration_seconds=duration_seconds
        )
        
        return breakdown


def run_async(coro):
    """Helper to run async functions in Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="CINEGEN Chat",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 CINEGEN Story Director Chat")
    st.markdown("*Duration-aware interactive storytelling for Veo 3.1 & Sora video generation*")
    
    # Duration awareness banner
    st.info("⚡ **Duration-First Design:** Every scene is optimized for video generation time limits (5-60s)")
    
    # Initialize the chat UI
    if 'chat_ui' not in st.session_state:
        st.session_state.chat_ui = CinegenChatUI()
        st.session_state.messages = []
        st.session_state.session_started = False
    
    # Sidebar for session management
    with st.sidebar:
        st.header("⏱️ Duration Control")
        st.markdown("*Critical for video generation limits*")
        
        # Duration settings - MOST IMPORTANT CONTROL
        target_duration = st.number_input(
            "🎬 Scene Duration (seconds)", 
            min_value=5, 
            max_value=60, 
            value=30,
            step=1,
            help="Enter exact duration for Veo 3.1 and future Sora integration"
        )
        
        # Visual duration indicator
        if target_duration <= 15:
            st.success(f"✅ {target_duration}s - Optimal for quick scenes")
        elif target_duration <= 30:
            st.info(f"⚡ {target_duration}s - Standard scene length")
        elif target_duration <= 45:
            st.warning(f"⚠️ {target_duration}s - Long scene")
        else:
            st.error(f"🚨 {target_duration}s - Maximum duration")
        
        st.markdown("---")
        st.header("📝 Session Controls")
        
        # Start new session button
        if st.button("🎯 Start New Story Session"):
            with st.spinner("Starting new CINEGEN session..."):
                session_id = run_async(
                    st.session_state.chat_ui.start_new_session(
                        persona_ids=[],  # Dynamic detection enabled
                        target_duration=target_duration
                    )
                )
                st.session_state.session_started = True
                st.session_state.messages = []
                st.session_state.current_duration = target_duration
                st.success(f"✅ Session started with {target_duration}s scenes")
        
        # Session status
        if st.session_state.session_started:
            st.success("🟢 Session Active")
            if st.session_state.chat_ui.current_session_id:
                st.text(f"ID: {st.session_state.chat_ui.current_session_id[:8]}...")
                st.text(f"Duration: {getattr(st.session_state, 'current_duration', target_duration)}s per scene")
        else:
            st.warning("🟡 No Active Session")
        
        st.markdown("---")
        st.markdown("**🎭 Dynamic Persona Detection:** Automatically detects personas from your prompt")
        st.markdown("**🎨 Available Emotions:**")
        st.markdown("• Angry • Inspired • Neutral")
        st.markdown("• Reflective • Relief")
        
        st.markdown("---")
        st.markdown("**🎥 Video Generation:**")
        st.markdown("• Veo 3.1: 5-60s scenes")
        st.markdown("• Sora: Coming soon")
        st.markdown(f"• Current: **{target_duration}s** scenes")
    
    # Main chat area
    st.header("💬 Chat with CINEGEN")
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "breakdown" in message:
                # Display the professional breakdown
                breakdown = message["breakdown"]
                
                st.markdown(f"**🎬 Scene Breakdown**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🎬 Subject:** {breakdown.subject}")
                    st.markdown(f"**🏛️ Setting:** {breakdown.context_setting}")
                    st.markdown(f"**🎭 Action:** {breakdown.action}")
                    st.markdown(f"**⏱️ Duration:** {breakdown.duration_seconds}s")
                
                with col2:
                    st.markdown(f"**🎨 Style:** {breakdown.style_aesthetic}")
                    st.markdown(f"**📷 Camera:** {breakdown.camera_composition}")
                    st.markdown(f"**💡 Lighting:** {breakdown.lighting_ambience}")
                    st.markdown(f"**🔊 Audio:** {breakdown.audio_dialogue}")
                
                # Duration-specific pacing info
                st.markdown("---")
                col3, col4 = st.columns(2)
                with col3:
                    if breakdown.duration_seconds <= 15:
                        st.info("⚡ **Quick Scene** - Rapid pacing, focused action")
                    elif breakdown.duration_seconds <= 30:
                        st.success("🎯 **Standard Scene** - Balanced pacing")
                    else:
                        st.warning("📽️ **Extended Scene** - Slower pacing, detailed shots")
                
                with col4:
                    # Video generation readiness
                    st.markdown("**🎥 Generation Ready:**")
                    if breakdown.duration_seconds <= 60:
                        st.success("✅ Veo 3.1 Compatible")
                    else:
                        st.error("❌ Exceeds Veo limits")
                
                # Generation prompt in expandable section
                with st.expander("🎥 Final Video Generation Prompt", expanded=True):
                    st.code(breakdown.generation_prompt, language="text")
                
                # Timing details - prominently displayed
                if breakdown.pacing_notes:
                    with st.expander("⏱️ Timing & Pacing Strategy", expanded=True):
                        st.markdown(breakdown.pacing_notes)
                
                # Video Generation Button for historical messages
                st.markdown("---")
                if st.button("🎬 Generate Video with Veo 3.1", key=f"gen_video_hist_{idx}", type="primary"):
                    with st.spinner("🎥 Generating video with Veo 3.1... This may take a few minutes..."):
                        try:
                            # Import VeloClient
                            from video_clients.velo_client import VeloClient
                            
                            # Get video script from breakdown
                            video_script = run_async(
                                st.session_state.chat_ui.cinegen.get_video_generation_script(breakdown)
                            )
                            
                            # Generate video
                            velo_client = VeloClient()
                            async def generate():
                                async with velo_client as client:
                                    return await client.generate_video(video_script)
                            
                            result = run_async(generate())
                            
                            if result.get("success"):
                                st.success("✅ Video generated successfully!")
                                if result.get("video_url"):
                                    st.video(result["video_url"])
                                st.json(result)
                            else:
                                st.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
                                if "mock" in result.get("model", "").lower():
                                    st.info("💡 **Tip:** Set GOOGLE_SERVICE_ACCOUNT_KEY in .env for real Veo generation")
                        except Exception as e:
                            st.error(f"Error generating video: {str(e)}")

            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Describe your video scene..."):
        # Get current duration setting
        current_duration = target_duration
        
        # Add user message with duration context
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "duration": current_duration
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(f"**Scene Request ({current_duration}s):** {prompt}")
        
        # Process with CINEGEN
        with st.chat_message("assistant"):
            # Create a placeholder for streaming text
            message_placeholder = st.empty()
            
            # Show initial thinking message
            message_placeholder.markdown(f"🤖 **CINEGEN analyzing {current_duration}s scene...**")
            
            try:
                # Create a status container for live updates
                with st.status(f"Generating scene breakdown...", expanded=True) as status:
                    st.write("📝 Processing your request...")
                    
                    # Process the breakdown
                    breakdown = run_async(
                        st.session_state.chat_ui.process_prompt(prompt, current_duration)
                    )
                    
                    st.write("✅ Scene breakdown complete!")
                    status.update(label="Scene breakdown ready!", state="complete", expanded=False)
                
                # Clear the thinking message
                message_placeholder.empty()
                
                # Now display the breakdown with streaming effect
                st.markdown(f"**🎬 Scene Breakdown ({breakdown.duration_seconds}s)**")
                
                # Display each section with a small delay for streaming effect
                import time
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Stream each field
                    st.markdown(f"**🎬 Subject:**")
                    subject_placeholder = st.empty()
                    subject_placeholder.markdown(f"_{breakdown.subject}_")
                    
                    st.markdown(f"**🏛️ Setting:**")
                    setting_placeholder = st.empty()
                    setting_placeholder.markdown(f"_{breakdown.context_setting}_")
                    
                    st.markdown(f"**🎭 Action:**")
                    action_placeholder = st.empty()
                    action_placeholder.markdown(f"_{breakdown.action}_")
                    
                    st.markdown(f"**⏱️ Duration:** {breakdown.duration_seconds}s")
                
                with col2:
                    st.markdown(f"**🎨 Style:**")
                    style_placeholder = st.empty()
                    style_placeholder.markdown(f"_{breakdown.style_aesthetic}_")
                    
                    st.markdown(f"**📷 Camera:**")
                    camera_placeholder = st.empty()
                    camera_placeholder.markdown(f"_{breakdown.camera_composition}_")
                    
                    st.markdown(f"**💡 Lighting:**")
                    lighting_placeholder = st.empty()
                    lighting_placeholder.markdown(f"_{breakdown.lighting_ambience}_")
                    
                    st.markdown(f"**🔊 Audio:**")
                    audio_placeholder = st.empty()
                    audio_placeholder.markdown(f"_{breakdown.audio_dialogue}_")
                
                # Duration-specific pacing info
                st.markdown("---")
                col3, col4 = st.columns(2)
                with col3:
                    if breakdown.duration_seconds <= 15:
                        st.info("⚡ **Quick Scene** - Rapid pacing, focused action")
                    elif breakdown.duration_seconds <= 30:
                        st.success("🎯 **Standard Scene** - Balanced pacing")
                    else:
                        st.warning("📽️ **Extended Scene** - Slower pacing, detailed shots")
                
                with col4:
                    # Video generation readiness
                    st.markdown("**🎥 Generation Ready:**")
                    if breakdown.duration_seconds <= 60:
                        st.success("✅ Veo 3.1 Compatible")
                    else:
                        st.error("❌ Exceeds Veo limits")
                
                with st.expander("🎥 Final Video Generation Prompt", expanded=True):
                    # Stream the generation prompt
                    prompt_placeholder = st.empty()
                    prompt_placeholder.code(breakdown.generation_prompt, language="text")
                
                if breakdown.pacing_notes:
                    with st.expander("⏱️ Timing & Pacing Strategy", expanded=True):
                        pacing_placeholder = st.empty()
                        pacing_placeholder.markdown(breakdown.pacing_notes)
                
                # Video Generation Button
                st.markdown("---")
                if st.button("🎬 Generate Video with Veo 3.1", key=f"gen_video_{len(st.session_state.messages)}", type="primary"):
                    with st.spinner("🎥 Generating video with Veo 3.1... This may take a few minutes..."):
                        try:
                            # Import VeloClient
                            from video_clients.velo_client import VeloClient
                            
                            # Get video script from breakdown
                            video_script = run_async(
                                st.session_state.chat_ui.cinegen.get_video_generation_script(breakdown)
                            )
                            
                            # Generate video
                            velo_client = VeloClient()
                            async def generate():
                                async with velo_client as client:
                                    return await client.generate_video(video_script)
                            
                            result = run_async(generate())
                            
                            if result.get("success"):
                                st.success("✅ Video generated successfully!")
                                if result.get("video_url"):
                                    st.video(result["video_url"])
                                st.json(result)
                            else:
                                st.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
                                if "mock" in result.get("model", "").lower():
                                    st.info("💡 **Tip:** Set GOOGLE_SERVICE_ACCOUNT_KEY in .env for real Veo generation")
                        except Exception as e:
                            st.error(f"Error generating video: {str(e)}")
                
                # Store the breakdown for chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Professional breakdown for {current_duration}s scene:",
                    "breakdown": breakdown,
                    "duration": current_duration
                })
                
            except Exception as e:
                st.error(f"Error processing prompt: {str(e)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {str(e)}"
                })    # Footer
    st.markdown("---")
    st.markdown("*Powered by CINEGEN Enhanced Story Director with Gemini AI*")
    st.markdown("🎥 **Video Generation:** Veo 3.1 (5-60s) • Sora (Coming Soon)")
    st.markdown("⚡ **Duration-Optimized:** Every scene crafted for maximum generation compatibility")


if __name__ == "__main__":
    main()