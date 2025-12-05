<div align="center"><div align="center"># SoRa Core - Clean Video Generation Platform



# 🎬 AI Video Generation Platform

### *Create Personalized Videos with Your Own AI Avatar*

# 🎬 AI Video Generation PlatformA clean extraction of the core video generation functionality from the original SoRa platform, without UI dependencies or storyteller components. This provides a focused foundation for building video generation applications.

<br>

### *Create Personalized Videos with Your Own AI Avatar*

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)## Features

[![Google AI](https://img.shields.io/badge/Google-Gemini%20API-green.svg)](https://ai.google.dev)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)<br>

[![Status](https://img.shields.io/badge/Status-In%20Development-orange.svg)](#)

- **Multi-Provider Video Generation**: Support for Google Velo 3.1 with unified interface for future providers

<br>

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)- **Persona Management**: Create and manage personas with consent handling

*Transform text prompts into stunning 8-second videos featuring your own digital persona*

[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)- **Vector Embeddings**: Store and search visual content using embeddings

<br>

[![Google AI](https://img.shields.io/badge/Google-Gemini%20API-green.svg)](https://ai.google.dev)- **Background Jobs**: Asynchronous video generation processing

> **🚧 Project Status:** This platform is actively under development! We welcome collaborations, contributions, and feedback to improve the existing codebase. Join us in building the future of personalized AI video generation.

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)- **Storage Management**: Support for local, S3, and Supabase storage

<br>

<br>- **Clean API**: FastAPI-based REST interface



</div><br>



---## Quick Start



<br>*Transform text prompts into stunning 8-second videos featuring your own digital persona*



## 📖 &nbsp; Table of Contents### 1. Install Dependencies



<div style="margin-left: 40px; margin-right: 40px;"><br>



- [✨ What This Does](#-what-this-does)<br>```bash

- [🎯 Key Features](#-key-features)  

- [🚀 Quick Start](#-quick-start)pip install -r requirements.txt

- [👤 Creating Your Persona](#-creating-your-persona)

- [🎬 Generating Videos](#-generating-videos)</div>```

- [⚙️ How It Works](#️-how-it-works)

- [📋 Requirements](#-requirements)

- [🛠️ Installation](#️-installation)

- [🎭 Persona Management](#-persona-management)---### 2. Set Environment Variables

- [💡 Tips & Best Practices](#-tips--best-practices)

- [🔧 Troubleshooting](#-troubleshooting)

- [🤝 Contributing](#-contributing)

<br>```bash

</div>

# Required for video generation

<br>

## 📖 &nbsp; Table of Contentsexport GOOGLE_API_KEY="your-google-api-key"

---

export GOOGLE_PROJECT_ID="your-project-id"  # Optional, for Vertex AI

<br>

<div style="margin-left: 40px; margin-right: 40px;">

## ✨ &nbsp; What This Does

# Optional database configuration

<div style="margin-left: 40px; margin-right: 40px;">

- [✨ What This Does](#-what-this-does)export DATABASE_URL="postgresql://localhost:5432/sora_core"

This AI-powered platform allows you to **create personalized video content** by simply describing what you want to see. The system uses your uploaded photos to generate a digital persona, then creates videos featuring *you* in any scenario you can imagine.

- [🎯 Key Features](#-key-features)  export REDIS_URL="redis://localhost:6379"

**Example:** Type *"Person working at a modern desk, focused and productive"* → Get an 8-second video of your AI avatar working at a desk!

- [🚀 Quick Start](#-quick-start)```

<br>

- [👤 Creating Your Persona](#-creating-your-persona)

### 🎪 &nbsp; Live Demo

- [🎬 Generating Videos](#-generating-videos)### 3. Run the API

```

Input:  "John presenting an innovative idea with excitement and confidence"- [⚙️ How It Works](#️-how-it-works)

Output: 8-second video of your persona presenting with animated gestures

```- [📋 Requirements](#-requirements)```python



</div>- [🛠️ Installation](#️-installation)from sora_core import create_app



<br>- [🎭 Persona Management](#-persona-management)import uvicorn



---- [💡 Tips & Best Practices](#-tips--best-practices)



<br>- [🔧 Troubleshooting](#-troubleshooting)app = create_app()



## 🎯 &nbsp; Key Features- [🤝 Contributing](#-contributing)



<div style="margin-left: 40px; margin-right: 40px;">if __name__ == "__main__":



<table></div>    uvicorn.run(app, host="0.0.0.0", port=8000)

<tr>

<td width="50%">```



### 🎭 **Dynamic Persona System**<br>

- Upload photos to create your digital avatar

- 5 emotional states: neutral, inspired, reflective, angry, relief### 4. Test Video Generation

- **Automatic name detection** from persona metadata

- Unlimited personas supported---



</td>```python

<td width="50%">

<br>import asyncio

### 🎬 **Video Generation**

- 8-second high-quality videosfrom sora_core import UnifiedVideoClient

- Google Veo 3.1 integration

- Reference image-guided generation## ✨ &nbsp; What This Does

- Multiple scenarios and settings

async def test_generation():

</td>

</tr><div style="margin-left: 40px; margin-right: 40px;">    client = UnifiedVideoClient()

<tr>

<td width="50%">    



### 🧠 **Smart AI**This AI-powered platform allows you to **create personalized video content** by simply describing what you want to see. The system uses your uploaded photos to generate a digital persona, then creates videos featuring *you* in any scenario you can imagine.    script = {

- Gemini-powered story understanding

- Automatic scene breakdown        "prompt": "A person walking through a beautiful park",

- Emotion-aware image selection

- Context-aware video creation**Example:** Type *"Person working at a modern desk, focused and productive"* → Get an 8-second video of your AI avatar working at a desk!        "duration": 10



</td>    }

<td width="50%">

<br>    

### 💻 **User Experience**

- Beautiful Streamlit web interface    result = await client.generate_video(script)

- Real-time generation progress

- Command-line tools available### 🎪 &nbsp; Live Demo    print(f"Generated video: {result}")

- Automatic video saving



</td>

</tr>```asyncio.run(test_generation())

</table>

Input:  "John presenting an innovative idea with excitement and confidence"```

</div>

Output: 8-second video of your persona presenting with animated gestures

<br>

```## Core Components

---



<br>

</div>### Video Clients

## 🚀 &nbsp; Quick Start



<div style="margin-left: 40px; margin-right: 40px;">

<br>```python

### 1️⃣ &nbsp; **Clone & Install**

from sora_core import UnifiedVideoClient, VeloClient

```bash

# Clone the repository---

git clone https://github.com/yourusername/ai-video-generation.git

cd ai-video-generation# Unified client with automatic provider selection



# Create virtual environment<br>client = UnifiedVideoClient(preferred_provider="velo")

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate



# Install dependencies## 🎯 &nbsp; Key Features# Direct provider access

pip install -r requirements.txt

```velo_client = VeloClient(api_key="your-key")



### 2️⃣ &nbsp; **Setup API Keys**<div style="margin-left: 40px; margin-right: 40px;">```



```bash

# Copy environment template

copy .env.example .env<table>### Persona Management



# Edit .env file with your API keys<tr>

GEMINI_API_KEY=your_gemini_api_key_here

GOOGLE_PROJECT_ID=your_google_project_id<td width="50%">```python

GOOGLE_ACCESS_TOKEN=your_google_access_token_here

```from sora_core import PersonaCreator, VisionProcessor, StorageClient



### 3️⃣ &nbsp; **Create Your Persona**### 🎭 **Persona System**



```bash- Upload your photos to create a digital avatarcreator = PersonaCreator(

# Run the persona upload script

python scripts/upload_persona.py- 5 emotional states: neutral, inspired, reflective, angry, relief    storage_client=StorageClient(),



# Follow the prompts to upload your photos- Automatic persona detection in prompts    vision_processor=VisionProcessor()

```

- Multiple personas supported)

### 4️⃣ &nbsp; **Generate Your First Video**



```bash

# Start the web interface</td>persona = await creator.create_persona(

python start_cinegen_chat.py

<td width="50%">    name="John Doe",

# Or use command line

python generate_video.py "Your prompt here"    description="A friendly person",

```

### 🎬 **Video Generation**    consent_status="approved"

</div>

- 8-second high-quality videos)

<br>

- Google Veo 3.1 integration```

---

- Reference image-guided generation

<br>

- Multiple scenarios and settings### Background Workers

## 👤 &nbsp; Creating Your Persona



<div style="margin-left: 40px; margin-right: 40px;">

</td>```python

Your persona is the digital representation of yourself (or others) that will appear in generated videos.

</tr>from sora_core import GenerationWorker

<br>

<tr>

### 📸 &nbsp; **Photo Requirements**

<td width="50%">worker = GenerationWorker()

<table>

<tr>

<td width="30%">

### 🧠 **Smart AI**# Queue a video generation job

**Quality Standards:**

- High resolution (min 512x512)- Gemini-powered story understandingjob_id = await worker.queue_generation_job(

- Well-lit, clear visibility

- Front-facing or slight angle- Automatic scene breakdown    job_type="video",

- Uncluttered background

- Emotion-aware image selection    persona_ids=["persona_123"],

</td>

<td width="70%">- Context-aware video creation    prompt="A scenic video",



**Emotional States Needed:**    parameters={"quality": "hd", "duration": 30}

- **Neutral:** Relaxed, natural expression

- **Inspired:** Bright eyes, slight smile, engaged look  </td>)

- **Reflective:** Thoughtful, contemplative expression

- **Angry:** Intense, furrowed brow, serious<td width="50%">

- **Relief:** Peaceful, content, satisfied smile

# Start processing

</td>

</tr>### 💻 **User Experience**await worker.start_worker()

</table>

- Beautiful Streamlit web interface```

<br>

- Real-time generation progress

### 📁 &nbsp; **Folder Structure**

- Command-line tools available## API Endpoints

```

personas/- Automatic video saving

└── your_name/

    ├── metadata.json              # Your persona configuration### Health Check

    └── reference_frames/          # Your photos organized by emotion

        ├── neutral/               # 1-3 photos showing neutral expression</td>- `GET /health` - System health and component status

        ├── inspired/              # 1-3 photos showing inspiration  

        ├── reflective/            # 1-3 photos showing reflection</tr>

        ├── angry/                 # 1-3 photos showing intensity

        └── relief/                # 1-3 photos showing contentment</table>### Personas

```

- `POST /personas` - Create new persona

<br>

</div>- `GET /personas/{id}` - Get persona details

### ⚙️ &nbsp; **Setup Methods**

- `GET /personas` - List personas

<details>

<summary><b>🤖 Automated Setup (Recommended)</b></summary><br>- `POST /personas/{id}/upload` - Upload files for persona



<br>- `DELETE /personas/{id}` - Delete persona



```bash---

# Run the interactive setup script

python scripts/upload_persona.py### Video Generation



# Follow the prompts:<br>- `POST /generate/video` - Queue video generation job

# 1. Enter your name

# 2. Select photos for each emotion- `GET /generate/jobs/{id}` - Get job status

# 3. Confirm upload

# 4. Wait for processing## 🚀 &nbsp; Quick Start- `DELETE /generate/jobs/{id}` - Cancel job

```

- `GET /generate/jobs` - List jobs

</details>

<div style="margin-left: 40px; margin-right: 40px;">

<details>

<summary><b>🔧 Manual Setup</b></summary>### Providers



<br>### 1️⃣ &nbsp; **Clone & Install**- `GET /providers` - Get available video providers



```bash- `POST /validate/script` - Validate generation script

# 1. Copy template structure

cp -r personas/example_persona/ personas/your_name/```bash



# 2. Edit metadata.json# Clone the repository## Configuration

# 3. Add your photos to emotion folders

# 4. Run upload scriptgit clone https://github.com/yourusername/ai-video-generation.git

python scripts/upload_persona.py

```cd ai-video-generationThe system uses environment variables for configuration:



</details>



</div># Create virtual environment```python



<br>python -m venv venvfrom sora_core import settings



---source venv/bin/activate  # On Windows: venv\Scripts\activate



<br># Access configuration



## 🎬 &nbsp; Generating Videos# Install dependenciesprint(f"API Host: {settings.api_host}")



<div style="margin-left: 40px; margin-right: 40px;">pip install -r requirements.txtprint(f"Google API Key configured: {bool(settings.google_api_key)}")



### 🖥️ &nbsp; **Web Interface (Recommended)**``````



```bash

# Start the Streamlit app

python start_cinegen_chat.py### 2️⃣ &nbsp; **Setup API Keys**## Mock Mode



# Navigate to http://localhost:8501

# Enter your prompt and watch the magic happen!

``````bashWhen external dependencies aren't available (API keys, databases), the system gracefully falls back to mock responses:



<br># Copy environment template



### ⌨️ &nbsp; **Command Line**copy .env.example .env- **No Google API Key**: Returns mock video URLs



```bash- **No Database**: Uses in-memory storage

# Generate a video

python generate_video.py "Person working at a modern desk, focused and productive"# Edit .env file with your API keys- **No Vector Store**: Returns mock similarity results



# Check generation statusGEMINI_API_KEY=your_gemini_api_key_here- **No Vision Models**: Generates deterministic mock captions/embeddings

python scripts/check_veo_operation.py "operation-id-from-above"

GOOGLE_PROJECT_ID=your_google_project_id

# Videos save automatically to output/videos/

```GOOGLE_ACCESS_TOKEN=your_google_access_token_here## Architecture



<br>```



### 📝 &nbsp; **Prompt Examples**```



<table>### 3️⃣ &nbsp; **Create Your Persona**sora_core/

<tr>

<td width="50%">├── config/          # Configuration management



**🏢 Professional Settings:**```bash├── video_clients/   # Video generation providers

- "Sarah presenting to a camera with confidence"

- "Alex working at a modern desk, focused"# Run the persona upload script├── storage/         # Database, vector store, file storage

- "Maria explaining an idea in a meeting room"

python scripts/upload_persona.py├── ingest/          # Persona creation and media processing

</td>

<td width="50%">├── worker/          # Background job processing



**🌅 Creative Scenarios:**# Follow the prompts to upload your photos└── api/             # FastAPI interface

- "John walking through a beautiful park"

- "Emma having a breakthrough moment"``````

- "David celebrating a success outdoors"



</td>

### 4️⃣ &nbsp; **Generate Your First Video**

```bash
# Start the web interface
python start_cinegen_chat.py

# Or use command line
python generate_video.py "Your prompt here"
```

</div>

<br>

---

<br>

## 👤 &nbsp; Creating Your Persona

<div style="margin-left: 40px; margin-right: 40px;">

**No hardcoding required!** Simply mention the persona name from your `metadata.json` file.

``````

<br>



### 🎯 &nbsp; **Prompt Tips**

</div>## Environment Variables

- ✅ **Include emotion:** "focused", "excited", "thoughtful", "confident"

- ✅ **Set the scene:** "modern office", "creative studio", "outdoor setting"  

- ✅ **Mention any persona name:** System reads from your personas folder

- ✅ **Keep it 8 seconds:** Perfect length for the AI model<br>| Variable | Description | Default |

- ❌ **Avoid:** Dangerous situations, explicit content, illegal activities

|----------|-------------|---------|

</div>

---| `GOOGLE_API_KEY` | Google API key for Velo 3.1 | None (mock mode) |

<br>

| `GOOGLE_PROJECT_ID` | Google Cloud project ID | "" |

---

<br>| `DATABASE_URL` | PostgreSQL connection string | Local PostgreSQL |

<br>

| `REDIS_URL` | Redis connection string | Local Redis |

## ⚙️ &nbsp; How It Works

## 👤 &nbsp; Creating Your Persona| `VECTOR_STORE_TYPE` | Vector store type (chroma/supabase) | chroma |

<div style="margin-left: 40px; margin-right: 40px;">

| `STORAGE_TYPE` | Storage type (local/s3/supabase) | local |

<br>

<div style="margin-left: 40px; margin-right: 40px;">

### 🔄 &nbsp; **Processing Pipeline**

## License

<table>

<tr>Your persona is the digital representation of yourself (or others) that will appear in generated videos.

<td width="25%">

This is a clean extraction focusing on core video generation functionality. The original codebase may have additional licensing considerations.

**1. Persona Upload**<br>

- Extract frames from your photos

- Classify emotional states### 📸 &nbsp; **Photo Requirements**

- Create vector embeddings

- Store in database<table>

<tr>

</td><td width="30%">

<td width="25%">

**Quality Standards:**

**2. Prompt Analysis**- High resolution (min 512x512)

- **Dynamically detect any persona names**- Well-lit, clear visibility

- Analyze emotional context- Front-facing or slight angle

- Break down scene elements- Uncluttered background

- Select appropriate emotion

</td>

</td><td width="70%">

<td width="25%">

**Emotional States Needed:**

**3. Image Retrieval**- **Neutral:** Relaxed, natural expression

- Query vector database- **Inspired:** Bright eyes, slight smile, engaged look  

- Find matching expressions- **Reflective:** Thoughtful, contemplative expression

- Select 3 best references- **Angry:** Intense, furrowed brow, serious

- Prepare for generation- **Relief:** Peaceful, content, satisfied smile



</td></td>

<td width="25%"></tr>

</table>

**4. Video Creation**

- Send to Google Veo 3.1<br>

- Generate 8-second video

- Apply your persona### 📁 &nbsp; **Folder Structure**

- Save final result

```

</td>personas/

</tr>└── your_name/

</table>    ├── metadata.json              # Your persona configuration

    └── reference_frames/          # Your photos organized by emotion

</div>        ├── neutral/               # 1-3 photos showing neutral expression

        ├── inspired/              # 1-3 photos showing inspiration  

<br>        ├── reflective/            # 1-3 photos showing reflection

        ├── angry/                 # 1-3 photos showing intensity

---        └── relief/                # 1-3 photos showing contentment

```

<br>

<br>

## 📋 &nbsp; Requirements

### ⚙️ &nbsp; **Setup Methods**

<div style="margin-left: 40px; margin-right: 40px;">

<details>

### 🔑 &nbsp; **API Keys Required**<summary><b>🤖 Automated Setup (Recommended)</b></summary>



<table><br>

<tr>

<td width="50%">```bash

# Run the interactive setup script

**🧠 Gemini API Key**python scripts/upload_persona.py

- Used for: Story analysis and prompt understanding

- Get it: [Google AI Studio](https://aistudio.google.com/)# Follow the prompts:

- Free tier: Available with limits# 1. Enter your name

# 2. Select photos for each emotion

</td># 3. Confirm upload

<td width="50%"># 4. Wait for processing

```

**☁️ Google Cloud Access**

- Used for: Video generation with Veo 3.1</details>

- Get it: [Google Cloud Console](https://console.cloud.google.com/)

- Note: Requires Google Cloud project and billing<details>

<summary><b>🔧 Manual Setup</b></summary>

</td>

</tr><br>

</table>

```bash

<br># 1. Copy template structure

cp -r personas/example_persona/ personas/your_name/

### 💻 &nbsp; **System Requirements**

# 2. Edit metadata.json

- **Python:** 3.8 or higher# 3. Add your photos to emotion folders

- **RAM:** 4GB minimum, 8GB recommended# 4. Run upload script

- **Storage:** 2GB free space (for videos and embeddings)python scripts/upload_persona.py

- **Internet:** Stable connection for API calls```



<br></details>



### 📦 &nbsp; **Dependencies**</div>



All dependencies are listed in `requirements.txt` and include:<br>

- `streamlit` - Web interface

- `google-generativeai` - Gemini integration  ---

- `chromadb` - Vector database

- `opencv-python` - Image processing<br>

- `requests` - API communications

## 🎬 &nbsp; Generating Videos

</div>

<div style="margin-left: 40px; margin-right: 40px;">

<br>

### 🖥️ &nbsp; **Web Interface (Recommended)**

---

```bash

<br># Start the Streamlit app

python start_cinegen_chat.py

## 🛠️ &nbsp; Installation

# Navigate to http://localhost:8501

<div style="margin-left: 40px; margin-right: 40px;"># Enter your prompt and watch the magic happen!

```

### 🐍 &nbsp; **Standard Installation**

<br>

```bash

# Clone repository### ⌨️ &nbsp; **Command Line**

git clone https://github.com/yourusername/ai-video-generation.git

cd ai-video-generation```bash

# Generate a video

# Create virtual environment (recommended)python generate_video.py "Person working at a modern desk, focused and productive"

python -m venv venv

# Check generation status

# Activate virtual environmentpython scripts/check_veo_operation.py "operation-id-from-above"

# Windows:

venv\Scripts\activate# Videos save automatically to output/videos/

# macOS/Linux:```

source venv/bin/activate

<br>

# Install dependencies

pip install -r requirements.txt### 📝 &nbsp; **Prompt Examples**

```

<table>

<br><tr>

<td width="50%">

### 🔧 &nbsp; **Configuration**

**🏢 Professional Settings:**

```bash- "Person presenting to a camera with confidence"

# Copy environment template- "Someone working at a modern desk, focused"

cp .env.example .env- "Person explaining an idea in a meeting room"



# Edit with your preferred editor</td>

nano .env  # or code .env, vim .env, etc.<td width="50%">



# Required variables:**🌅 Creative Scenarios:**

GEMINI_API_KEY=your_key_here- "Person walking through a beautiful park"

GOOGLE_PROJECT_ID=your_project_id- "Someone having a breakthrough moment"

GOOGLE_ACCESS_TOKEN=your_access_token- "Person celebrating a success outdoors"

```

</td>

</div></tr>

</table>

<br>

<br>

---

### 💡 &nbsp; **Prompt Tips**

<br>

- ✅ **Include emotion:** "focused", "excited", "thoughtful", "confident"

## 🎭 &nbsp; Persona Management- ✅ **Set the scene:** "modern office", "creative studio", "outdoor setting"  

- ✅ **Mention your name:** "John working..." (triggers persona detection)

<div style="margin-left: 40px; margin-right: 40px;">- ✅ **Keep it 8 seconds:** Perfect length for the AI model

- ❌ **Avoid:** Dangerous situations, explicit content, illegal activities

### 👥 &nbsp; **Multiple Personas**

</div>

You can create and manage unlimited personas for different people:

<br>

```bash

personas/---

├── sarah/         # Sarah's persona

├── alex/          # Alex's persona  <br>

├── maria/         # Maria's persona

├── david/         # David's persona## ⚙️ &nbsp; How It Works

└── team_lead/     # Professional persona

```<div style="margin-left: 40px; margin-right: 40px;">



<br><br>



### 🔄 &nbsp; **Managing Personas**### 🔄 &nbsp; **Processing Pipeline**



<table><table>

<tr><tr>

<td width="50%"><td width="25%">



**Create New Persona:****1. Persona Upload**

```bash- Extract frames from your photos

python scripts/upload_persona.py- Classify emotional states

# Follow prompts for new person- Create vector embeddings

```- Store in database



**Update Existing:**</td>

```bash<td width="25%">

# Add new photos to emotion folders

# Re-run upload script**2. Prompt Analysis**

python scripts/upload_persona.py- Detect persona mentions

```- Analyze emotional context

- Break down scene elements

</td>- Select appropriate emotion

<td width="50%">

</td>

**Check Persona Status:**<td width="25%">

```bash

python scripts/debug_chromadb.py**3. Image Retrieval**

# Shows all uploaded personas- Query vector database

```- Find matching expressions

- Select 3 best references

**Remove Persona:**- Prepare for generation

```bash

# Delete persona folder</td>

rm -rf personas/persona_name/<td width="25%">

```

**4. Video Creation**

</td>- Send to Google Veo 3.1

</tr>- Generate 8-second video

</table>- Apply your persona

- Save final result

<br>

</td>

### 🎯 &nbsp; **Dynamic Persona Detection**</tr>

</table>

The system automatically detects **any persona** mentioned in prompts by reading from your personas folder:

</div>

```bash

"Sarah working at her desk"     → Uses Sarah's persona<br>

"Alex presenting an idea"       → Uses Alex's persona  

"Maria in a meeting room"       → Uses Maria's persona---

"David celebrating success"     → Uses David's persona

```<br>



**Key Features:**## 📋 &nbsp; Requirements

- 🔄 **No hardcoding** - reads directly from `metadata.json` files

- 🎯 **Name variations** - supports aliases defined in metadata<div style="margin-left: 40px; margin-right: 40px;">

- 🌐 **Case insensitive** - "sarah", "Sarah", "SARAH" all work

- 📁 **Folder-based** - persona name = folder name### 🔑 &nbsp; **API Keys Required**



</div><table>

<tr>

<br><td width="50%">



---**🧠 Gemini API Key**

- Used for: Story analysis and prompt understanding

<br>- Get it: [Google AI Studio](https://aistudio.google.com/)

- Free tier: Available with limits

## 💡 &nbsp; Tips & Best Practices

</td>

<div style="margin-left: 40px; margin-right: 40px;"><td width="50%">



### 📸 &nbsp; **Photo Quality Tips****☁️ Google Cloud Access**

- Used for: Video generation with Veo 3.1

<table>- Get it: [Google Cloud Console](https://console.cloud.google.com/)

<tr>- Note: Requires Google Cloud project and billing

<td width="50%">

</td>

**✅ Best Practices:**</tr>

- Use natural lighting (avoid harsh shadows)</table>

- Include some variety in angles (not all identical)

- Ensure clear facial features are visible<br>

- Use recent, high-quality photos

- Keep backgrounds simple and uncluttered### 💻 &nbsp; **System Requirements**



</td>- **Python:** 3.8 or higher

<td width="50%">- **RAM:** 4GB minimum, 8GB recommended

- **Storage:** 2GB free space (for videos and embeddings)

**❌ Avoid These:**- **Internet:** Stable connection for API calls

- Blurry or low-resolution images

- Heavy filters or editing<br>

- Sunglasses or face coverings

- Extreme angles or lighting### 📦 &nbsp; **Dependencies**

- Busy, distracting backgrounds

All dependencies are listed in `requirements.txt` and include:

</td>- `streamlit` - Web interface

</tr>- `google-generativeai` - Gemini integration  

</table>- `chromadb` - Vector database

- `opencv-python` - Image processing

<br>- `requests` - API communications



### 🎬 &nbsp; **Video Generation Tips**</div>



- **Be Specific:** "Person working at a modern desk" vs "Person working"<br>

- **Include Context:** Mention the setting, mood, and activity

- **Use Any Name:** System automatically detects all personas---

- **Keep It Simple:** Complex scenarios may not translate well

- **Iterate:** Try variations of prompts for different results<br>



<br>## 🛠️ &nbsp; Installation



### ⚡ &nbsp; **Performance Optimization**<div style="margin-left: 40px; margin-right: 40px;">



- **Batch Operations:** Upload multiple personas at once### 🐍 &nbsp; **Standard Installation**

- **Image Size:** Optimize images to 1024x1024 for best results

- **API Limits:** Be mindful of Google Cloud quotas```bash

- **Storage:** Regularly clean up generated videos to save space# Clone repository

git clone https://github.com/yourusername/ai-video-generation.git

</div>cd ai-video-generation



<br># Create virtual environment (recommended)

python -m venv venv

---

# Activate virtual environment

<br># Windows:

venv\Scripts\activate

## 🔧 &nbsp; Troubleshooting# macOS/Linux:

source venv/bin/activate

<div style="margin-left: 40px; margin-right: 40px;">

# Install dependencies

<details>pip install -r requirements.txt

<summary><b>🔑 API Key Issues</b></summary>```



<br><br>



**Problem:** "API key not found" or authentication errors### 🔧 &nbsp; **Configuration**



**Solutions:**```bash

- Check `.env` file exists and has correct format# Copy environment template

- Verify API keys are valid and activecp .env.example .env

- Ensure no extra spaces or quotes around keys

- Test API access with a simple script# Edit with your preferred editor

nano .env  # or code .env, vim .env, etc.

```bash

# Test Gemini API# Required variables:

python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('API works!')"GEMINI_API_KEY=your_key_here

```GOOGLE_PROJECT_ID=your_project_id

GOOGLE_ACCESS_TOKEN=your_access_token

</details>```



<details></div>

<summary><b>👤 Persona Problems</b></summary>

<br>

<br>

---

**Problem:** Persona not detected or "No personas found"

<br>

**Solutions:**

- Check persona folder structure matches requirements## 🎭 &nbsp; Persona Management

- Verify `metadata.json` is valid JSON format

- Ensure reference images exist in emotion subfolders<div style="margin-left: 40px; margin-right: 40px;">

- Run persona upload script again

### 👥 &nbsp; **Multiple Personas**

```bash

# Debug persona statusYou can create and manage multiple personas for different people:

python scripts/debug_chromadb.py

``````bash

personas/

</details>├── john/          # First persona

├── sarah/         # Second persona  

<details>├── alex/          # Third persona

<summary><b>🎬 Video Generation Failures</b></summary>└── team_lead/     # Professional persona

```

<br>

<br>

**Problem:** Videos fail to generate or timeout

### 🔄 &nbsp; **Managing Personas**

**Solutions:**

- Check internet connection stability<table>

- Verify Google Cloud project has billing enabled<tr>

- Check API quotas and limits<td width="50%">

- Try simpler prompts first

- Wait for rate limits to reset**Create New Persona:**

```bash

</details>python scripts/upload_persona.py

# Follow prompts for new person

<details>```

<summary><b>💾 Storage Issues</b></summary>

**Update Existing:**

<br>```bash

# Add new photos to emotion folders

**Problem:** Out of space or file access errors# Re-run upload script

python scripts/upload_persona.py

**Solutions:**```

- Clean up old videos in `output/videos/`

- Check disk space availability</td>

- Verify write permissions on directories<td width="50%">

- Consider external storage for large collections

**Check Persona Status:**

</details>```bash

python scripts/debug_chromadb.py

</div># Shows all uploaded personas

```

<br>

**Remove Persona:**

---```bash

# Delete persona folder

<br>rm -rf personas/persona_name/

```

## 🤝 &nbsp; Contributing

</td>

<div style="margin-left: 40px; margin-right: 40px;"></tr>

</table>

We welcome contributions to improve this AI video generation platform!

<br>

<br>

### 🎯 &nbsp; **Persona Detection**

### 🚀 &nbsp; **How to Contribute**

The system automatically detects personas mentioned in prompts:

1. **Fork** the repository

2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)```bash

3. **Commit** your changes (`git commit -m 'Add amazing feature'`)"John working at his desk"     → Uses John's persona

4. **Push** to the branch (`git push origin feature/amazing-feature`)"Sarah presenting an idea"     → Uses Sarah's persona  

5. **Open** a Pull Request"Person walking in park"       → Uses default/first available persona

```

<br>

</div>

### 🎯 &nbsp; **Areas for Contribution**

<br>

- **New Video Providers:** Add support for other AI video services

- **UI Improvements:** Enhance the Streamlit interface---

- **Performance:** Optimize image processing and API calls

- **Documentation:** Improve guides and tutorials<br>

- **Dynamic Features:** Improve persona detection and management

- **Testing:** Add automated tests and validation## 💡 &nbsp; Tips & Best Practices



<br><div style="margin-left: 40px; margin-right: 40px;">



### 🌟 &nbsp; **Priority Areas**### 📸 &nbsp; **Photo Quality Tips**



- **Enhanced Persona System:** Better emotion detection and classification<table>

- **Video Quality:** Improve generation consistency and quality<tr>

- **User Experience:** Streamline setup and usage workflows<td width="50%">

- **Multi-Provider Support:** Add Sora, RunwayML, and other video AI services

- **Real-time Processing:** Reduce generation times and improve feedback**✅ Best Practices:**

- Use natural lighting (avoid harsh shadows)

<br>- Include some variety in angles (not all identical)

- Ensure clear facial features are visible

### 📝 &nbsp; **Development Guidelines**- Use recent, high-quality photos

- Keep backgrounds simple and uncluttered

- Follow PEP 8 style guidelines

- Add docstrings to new functions</td>

- Test with multiple personas before submitting<td width="50%">

- Update documentation for new features

- Ensure backward compatibility**❌ Avoid These:**

- Blurry or low-resolution images

</div>- Heavy filters or editing

- Sunglasses or face coverings

<br>- Extreme angles or lighting

- Busy, distracting backgrounds

---

</td>

<br></tr>

</table>

<div align="center">

<br>

### 🎬 Ready to Create Your AI Videos?

### 🎬 &nbsp; **Video Generation Tips**

<br>

- **Be Specific:** "Person working at a modern desk" vs "Person working"

**[⬇️ Clone Repository](https://github.com/yourusername/ai-video-generation)** • **[📖 Read Setup Guide](SETUP.md)** • **[🎭 Create Persona](personas/README.md)**- **Include Context:** Mention the setting, mood, and activity

- **Use Names:** Include persona names for automatic detection

<br>- **Keep It Simple:** Complex scenarios may not translate well

- **Iterate:** Try variations of prompts for different results

---

<br>

*Built with ❤️ using Google's Gemini AI and Veo 3.1*

### ⚡ &nbsp; **Performance Optimization**

*🚧 Under active development - Contributors welcome!*

- **Batch Operations:** Upload multiple personas at once

<br>- **Image Size:** Optimize images to 1024x1024 for best results

- **API Limits:** Be mindful of Google Cloud quotas

[![Star this repo](https://img.shields.io/github/stars/yourusername/ai-video-generation?style=social)](https://github.com/yourusername/ai-video-generation/stargazers)- **Storage:** Regularly clean up generated videos to save space



</div></div>

<br>

---

<br>

## 🔧 &nbsp; Troubleshooting

<div style="margin-left: 40px; margin-right: 40px;">

<details>
<summary><b>🔑 API Key Issues</b></summary>

<br>

**Problem:** "API key not found" or authentication errors

**Solutions:**
- Check `.env` file exists and has correct format
- Verify API keys are valid and active
- Ensure no extra spaces or quotes around keys
- Test API access with a simple script

```bash
# Test Gemini API
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('API works!')"
```

</details>

<details>
<summary><b>👤 Persona Problems</b></summary>

<br>

**Problem:** Persona not detected or "No personas found"

**Solutions:**
- Check persona folder structure matches requirements
- Verify `metadata.json` is valid JSON format
- Ensure reference images exist in emotion subfolders
- Run persona upload script again

```bash
# Debug persona status
python scripts/debug_chromadb.py
```

</details>

<details>
<summary><b>🎬 Video Generation Failures</b></summary>

<br>

**Problem:** Videos fail to generate or timeout

**Solutions:**
- Check internet connection stability
- Verify Google Cloud project has billing enabled
- Check API quotas and limits
- Try simpler prompts first
- Wait for rate limits to reset

</details>

<details>
<summary><b>💾 Storage Issues</b></summary>

<br>

**Problem:** Out of space or file access errors

**Solutions:**
- Clean up old videos in `output/videos/`
- Check disk space availability
- Verify write permissions on directories
- Consider external storage for large collections

</details>

</div>

<br>

---

<br>

## 🤝 &nbsp; Contributing

<div style="margin-left: 40px; margin-right: 40px;">

We welcome contributions to improve this AI video generation platform!

<br>

### 🚀 &nbsp; **How to Contribute**

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

<br>

### 🎯 &nbsp; **Areas for Contribution**

- **New Video Providers:** Add support for other AI video services
- **UI Improvements:** Enhance the Streamlit interface
- **Performance:** Optimize image processing and API calls
- **Documentation:** Improve guides and tutorials
- **Testing:** Add automated tests and validation

<br>

### 📝 &nbsp; **Development Guidelines**

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Test with multiple personas before submitting
- Update documentation for new features

</div>

<br>

---

<br>

<div align="center">

### 🎬 Ready to Create Your AI Videos?

<br>

**[⬇️ Clone Repository](https://github.com/yourusername/ai-video-generation)** • **[📖 Read Setup Guide](SETUP.md)** • **[🎭 Create Persona](personas/README.md)**

<br>

---

*Built with ❤️ using Google's Gemini AI and Veo 3.1*

<br>

[![Star this repo](https://img.shields.io/github/stars/yourusername/ai-video-generation?style=social)](https://github.com/yourusername/ai-video-generation/stargazers)

</div>