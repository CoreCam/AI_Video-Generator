"""
Core configuration settings for SoRa video generation platform.
Cleaned version focusing on essential settings.
"""
import os
from pathlib import Path
from typing import Optional

class CoreSettings:
    """Core application settings for video generation platform."""
    
    def __init__(self):
        self.load_from_env()
    
    def load_from_env(self):
        """Load settings from environment variables."""
        
        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Google AI Configuration (Primary for Video Generation)
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_project_id = os.getenv("GOOGLE_PROJECT_ID", "")
        self.google_location = os.getenv("GOOGLE_LOCATION", "us-central1")
        
        # Velo Configuration for Video Generation
        self.velo_model_name = os.getenv("VELO_MODEL_NAME", "velo-3.1")
        self.vertex_api_endpoint = os.getenv(
            "VERTEX_API_ENDPOINT", 
            "https://us-central1-aiplatform.googleapis.com/v1beta1"
        )
        
        # Video Generation Preferences
        self.preferred_video_provider = os.getenv("PREFERRED_VIDEO_PROVIDER", "auto")
        self.video_fallback_enabled = os.getenv("VIDEO_FALLBACK_ENABLED", "true").lower() == "true"
        
        # Database Configuration
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://localhost:5432/sora_core"
        )
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Redis Configuration
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Vector Store Configuration
        self.chroma_url = os.getenv("CHROMA_URL", "http://localhost:8000")
        self.vector_store_type = os.getenv("VECTOR_STORE_TYPE", "chroma")
        
        # Storage Configuration
        self.storage_type = os.getenv("STORAGE_TYPE", "local")
        self.s3_bucket = os.getenv("S3_BUCKET", "sora-core")
        self.s3_access_key = os.getenv("S3_ACCESS_KEY")
        self.s3_secret_key = os.getenv("S3_SECRET_KEY")
        self.s3_region = os.getenv("S3_REGION", "us-east-1")
        
        # Vision Model Configuration
        self.vision_model_type = os.getenv("VISION_MODEL_TYPE", "clip")
        self.vision_model_device = os.getenv("VISION_MODEL_DEVICE", "cpu")
        
        # Worker Configuration
        self.worker_count = int(os.getenv("WORKER_COUNT", "1"))
        self.job_timeout = int(os.getenv("JOB_TIMEOUT", "3600"))
        
        # Security and Privacy
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "100"))
        
        # Consent and Compliance
        self.require_consent = os.getenv("REQUIRE_CONSENT", "true").lower() == "true"
        self.consent_expiry_days = int(os.getenv("CONSENT_EXPIRY_DAYS", "365"))
        self.data_retention_days = int(os.getenv("DATA_RETENTION_DAYS", "730"))
        
        # Application Paths
        self.base_dir = Path(__file__).parent.parent
        self.upload_dir = self.base_dir / "data" / "uploads"
        self.output_dir = self.base_dir / "data" / "outputs"
        self.log_dir = self.base_dir / "logs"
        
        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_configuration(self) -> bool:
        """Validate that required configuration is present."""
        if not self.google_api_key:
            print("Warning: GOOGLE_API_KEY not set - video generation will use mock responses")
            return False
        return True
    
    def get_video_config(self) -> dict:
        """Get video generation specific configuration."""
        return {
            "google_api_key": self.google_api_key,
            "google_project_id": self.google_project_id,
            "google_location": self.google_location,
            "velo_model_name": self.velo_model_name,
            "vertex_api_endpoint": self.vertex_api_endpoint,
            "preferred_provider": self.preferred_video_provider,
            "fallback_enabled": self.video_fallback_enabled
        }

# Global settings instance
settings = CoreSettings()