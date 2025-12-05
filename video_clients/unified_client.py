"""
Unified video generation client supporting multiple AI providers.
Clean extraction focusing on core video generation functionality.
"""
from typing import Dict, Any, List, Optional, Union
import asyncio
from datetime import datetime
from .sora_client import SoraClient
from .velo_client import VeloClient

class UnifiedVideoClient:
    """
    Unified client for multiple video generation providers.
    Routes requests to appropriate provider based on availability and preferences.
    """
    
    def __init__(self, preferred_provider: str = "auto"):
        self.preferred_provider = preferred_provider
        self.providers = {}
        self.fallback_order = ["velo", "sora"]  # Velo first since it's available now
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available video generation providers."""
        
        # Load settings for proper configuration
        try:
            from ..config.settings import settings
        except ImportError:
            # Fallback if settings not available
            import os
            class MockSettings:
                google_api_key = os.getenv("GOOGLE_API_KEY")
                google_project_id = os.getenv("GOOGLE_PROJECT_ID", "")
                google_location = os.getenv("GOOGLE_LOCATION", "us-central1")
            settings = MockSettings()
        
        try:
            self.providers["sora"] = SoraClient()
            print("[OK] Sora client initialized (mock mode)")
        except Exception as e:
            print(f"[ERROR] Sora client initialization failed: {e}")
        
        try:
            # Check if we should use reference images (full VEO model)
            import os
            use_reference_images = os.getenv("VEO_USE_REFERENCE_IMAGES", "true").lower() == "true"
            
            self.providers["velo"] = VeloClient(
                api_key=settings.google_api_key,
                project_id=settings.google_project_id,
                location=settings.google_location,
                use_reference_images=use_reference_images
            )
            
            if settings.google_api_key:
                print("[OK] Velo client initialized with real API key")
            else:
                print("[OK] Velo client initialized (demo mode)")
        except Exception as e:
            print(f"[ERROR] Velo client initialization failed: {e}")
    
    def get_client(self, provider: str):
        """Get a specific client instance."""
        return self.providers.get(provider)
    
    async def generate_video(
        self,
        script: Dict[str, Any],
        provider: str = None,
        quality: str = "hd",
        format: str = "mp4",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using the best available provider.
        
        Personas are automatically detected from the prompt text.
        No need to specify persona_name - the system will detect which personas
        are mentioned and load their reference images accordingly.
        
        Args:
            script: Generated script with scenes and prompts
            provider: Specific provider to use ("sora", "velo", or None for auto)
            quality: Video quality preference
            format: Output format preference
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generation result with provider information
        """
        
        # Determine which provider to use
        selected_provider = self._select_provider(provider)
        
        if not selected_provider:
            return {
                "success": False,
                "error": "No video generation providers available",
                "available_providers": list(self.providers.keys())
            }
        
        try:
            print(f"[INFO] Generating video using {selected_provider.upper()}")
            
            client = self.providers[selected_provider]
            
            # Add provider-specific optimizations
            optimized_kwargs = self._optimize_for_provider(selected_provider, kwargs)
            optimized_kwargs.update({
                "quality": quality,
                "format": format
            })
            
            # Generate video (personas auto-detected from prompt)
            result = await client.generate_video(script, **optimized_kwargs)
            
            # Add unified client metadata
            result["unified_client_version"] = "1.0.0"
            result["selected_provider"] = selected_provider
            result["provider_selection_reason"] = self._get_selection_reason(selected_provider, provider)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Video generation failed with {selected_provider}: {e}")
            
            # Try fallback if enabled and not already using fallback
            if provider is None and len(self.providers) > 1:
                return await self._try_fallback(script, selected_provider, quality, format, **kwargs)
            
            return {
                "success": False,
                "error": f"Video generation failed: {str(e)}",
                "provider": selected_provider
            }
    
    def _select_provider(self, requested_provider: str = None) -> Optional[str]:
        """Select the best available provider."""
        
        if requested_provider and requested_provider in self.providers:
            return requested_provider
        
        if self.preferred_provider != "auto" and self.preferred_provider in self.providers:
            return self.preferred_provider
        
        # Auto-select based on availability
        for provider in self.fallback_order:
            if provider in self.providers:
                client = self.providers[provider]
                if hasattr(client, 'api_key') and client.api_key:
                    return provider
                elif provider == "sora":  # Sora is always available in mock mode
                    return provider
        
        # Return first available as last resort
        return next(iter(self.providers.keys())) if self.providers else None
    
    def _get_selection_reason(self, selected: str, requested: str = None) -> str:
        """Get human-readable reason for provider selection."""
        
        if requested and requested == selected:
            return f"User requested {selected}"
        elif requested and requested != selected:
            return f"User requested {requested} but {selected} was selected due to availability"
        elif self.preferred_provider == selected:
            return f"Preferred provider {selected}"
        else:
            return f"Auto-selected {selected} based on availability"
    
    def _optimize_for_provider(self, provider: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply provider-specific optimizations."""
        
        optimized = kwargs.copy()
        
        if provider == "velo":
            # Velo-specific optimizations
            optimized.setdefault("temperature", 0.7)
            optimized.setdefault("aspect_ratio", "16:9")
            
        elif provider == "sora":
            # Sora-specific optimizations (when available)
            optimized.setdefault("style", "natural")
            
        return optimized
    
    async def _try_fallback(
        self,
        script: Dict[str, Any],
        failed_provider: str,
        quality: str,
        format: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Try fallback providers when primary fails."""
        
        print(f"[INFO] Trying fallback providers after {failed_provider} failed")
        
        remaining_providers = [p for p in self.fallback_order if p != failed_provider and p in self.providers]
        
        for provider in remaining_providers:
            try:
                print(f"[INFO] Attempting fallback to {provider}")
                
                client = self.providers[provider]
                optimized_kwargs = self._optimize_for_provider(provider, kwargs)
                optimized_kwargs.update({"quality": quality, "format": format})
                
                result = await client.generate_video(script, **optimized_kwargs)
                
                if result.get("success"):
                    result["fallback_used"] = True
                    result["original_provider"] = failed_provider
                    result["selected_provider"] = provider
                    result["provider_selection_reason"] = f"Fallback to {provider} after {failed_provider} failed"
                    
                    print(f"[SUCCESS] Fallback to {provider} successful")
                    return result
                
            except Exception as e:
                print(f"[ERROR] Fallback to {provider} also failed: {e}")
                continue
        
        return {
            "success": False,
            "error": f"All providers failed. Last error from {failed_provider}",
            "attempted_providers": [failed_provider] + remaining_providers
        }
    
    async def validate_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a script for video generation."""
        
        validation_result = {
            "valid": True,
            "issues": [],
            "suggestions": [],
            "provider_compatibility": {}
        }
        
        # Basic script validation
        if not script:
            validation_result["valid"] = False
            validation_result["issues"].append("Empty script provided")
            return validation_result
        
        # Check for required fields
        if "scenes" not in script and "prompt" not in script:
            validation_result["valid"] = False
            validation_result["issues"].append("Script must contain either 'scenes' or 'prompt'")
        
        # Validate individual providers
        for provider_name, client in self.providers.items():
            if hasattr(client, 'validate_prompt'):
                try:
                    # Extract prompt for validation
                    if "scenes" in script and script["scenes"]:
                        prompt = script["scenes"][0].get("description", "")
                    else:
                        prompt = script.get("prompt", "")
                    
                    if prompt:
                        provider_validation = await client.validate_prompt(prompt)
                        validation_result["provider_compatibility"][provider_name] = provider_validation
                except Exception as e:
                    validation_result["provider_compatibility"][provider_name] = {
                        "valid": False,
                        "error": str(e)
                    }
        
        return validation_result
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers with their status."""
        
        providers_info = []
        
        for provider_name, client in self.providers.items():
            try:
                status = client.get_status() if hasattr(client, 'get_status') else {}
                providers_info.append({
                    "name": provider_name,
                    "available": True,
                    **status
                })
            except Exception as e:
                providers_info.append({
                    "name": provider_name,
                    "available": False,
                    "error": str(e)
                })
        
        return providers_info
    
    def get_status(self) -> Dict[str, Any]:
        """Get unified client status."""
        
        return {
            "unified_client_version": "1.0.0",
            "preferred_provider": self.preferred_provider,
            "fallback_order": self.fallback_order,
            "providers": self.get_available_providers(),
            "total_providers": len(self.providers)
        }