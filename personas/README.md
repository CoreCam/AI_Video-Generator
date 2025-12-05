# 👤 Personas Directory

This directory stores persona data for AI video generation. Each persona represents a person who can appear in generated videos.

## 📂 Structure

```
personas/
├── README.md              # This file
├── example_persona/       # Template persona structure
│   ├── README.md         # Setup instructions
│   └── metadata.json     # Persona configuration template
├── your_persona_name/     # Your actual persona (create this)
│   ├── metadata.json     # Your persona details
│   ├── reference_frames/ # Reference images by emotion
│   │   ├── angry/
│   │   ├── inspired/
│   │   ├── neutral/
│   │   ├── reflective/
│   │   └── relief/
│   ├── videos/           # Generated videos (auto-created)
│   ├── embeddings/       # AI embeddings (auto-created)
│   └── processed/        # Processed data (auto-created)
└── chroma_db/            # Vector database (auto-created)
```

## 🚀 Getting Started

1. **Copy the template**:
   ```bash
   cp -r example_persona/ your_name/
   ```

2. **Edit metadata.json**:
   - Update `persona_id`, `name`, and `description`
   - Modify `video_files` list if needed

3. **Add reference images**:
   - Create subfolders in `reference_frames/` for each emotion
   - Add 1-3 clear photos per emotion showing that expression

4. **Upload your persona**:
   ```bash
   python scripts/upload_persona.py
   ```

## 📋 Metadata Format

Your `metadata.json` should follow this structure:

```json
{
  "persona_id": "unique_id_001",
  "name": "YourName",
  "description": "Brief description of this persona",
  "created_at": "2025-01-01T00:00:00Z",
  "video_files": [
    "yourname_angry.mp4",
    "yourname_inspired.mp4", 
    "yourname_neutral.mp4",
    "yourname_reflective.mp4",
    "yourname_relief.mp4"
  ],
  "appearance": {
    "facial_features": "Describe key features",
    "expressions": "5 distinct emotional states",
    "mannerisms": "Natural movement patterns",
    "consistency": "Recognizable across states"
  },
  "personality": {
    "speaking_style": "Natural and conversational",
    "tone": "Authentic and engaging", 
    "energy_level": "Adaptable based on context",
    "authenticity": "Real person with genuine expressions"
  },
  "emotional_range": {
    "angry": "Intense emotions, dramatic tension",
    "inspired": "Excitement, enthusiasm, discovery",
    "neutral": "Calm, natural baseline expression",
    "reflective": "Thoughtful, contemplative",
    "relief": "Satisfaction, peaceful resolution"
  },
  "embedding_status": "not_started",
  "vector_store_status": "not_uploaded"
}
```

## 🖼️ Reference Images

### Requirements:
- **Quality**: High resolution, well-lit, clear face
- **Angles**: Front-facing or slight angle preferred
- **Background**: Simple, non-distracting
- **Expression**: Clear emotional state matching folder name

### Emotions Guide:
- **angry**: Furrowed brow, tense jaw, intense gaze
- **inspired**: Bright eyes, slight smile, open expression
- **neutral**: Relaxed face, soft gaze, natural posture
- **reflective**: Thoughtful look, perhaps hand on chin
- **relief**: Peaceful smile, relaxed shoulders, content

## 🎬 Using Your Persona

Once uploaded, include your persona name in video prompts:

```
"John working at a modern desk, focused and productive"
"Sarah presenting an idea with enthusiasm and excitement"
"Alex walking through a beautiful park on a sunny day"
```

The system will automatically:
1. Detect your persona name in the prompt
2. Load appropriate reference images
3. Generate video featuring your persona

## 🔒 Privacy & Security

- **Never commit personal photos to version control**
- **Keep your `.env` file private** 
- **The `.gitignore` excludes persona folders** (except example)
- **Delete any test personas before sharing code**

## 🛠️ Troubleshooting

### "Persona not found"
- Check folder name matches metadata `persona_id`
- Verify `metadata.json` syntax is valid
- Ensure reference images exist in subfolders

### "No reference images"
- Add at least 1 image per emotion folder
- Check image formats (jpg, png, etc.)
- Verify folder names match exactly: `angry`, `inspired`, `neutral`, `reflective`, `relief`

### "Embedding failed"
- Check internet connection
- Verify API keys in `.env`
- Try re-running upload script

## 📞 Need Help?

1. Check the main `README.md` for project setup
2. Review `SETUP.md` for detailed instructions
3. Run test scripts to verify configuration
4. Check logs in the console for error details