# Persona Setup Instructions

This folder contains a template persona structure. To create your own persona:

1. **Create a new folder** for your persona (e.g., `personas/your_name/`)

2. **Copy the structure** from this example_persona folder

3. **Update metadata.json** with your persona details:
   - Change `persona_id` to a unique identifier
   - Update `name` and `description`
   - Modify `video_files` to match your actual emotions in the video files

4. **Add reference images** in `reference_frames/` folder:
   - Create subfolders: `angry/`, `inspired/`, `neutral/`, `reflective/`, `relief/`
   - Add 1-3 reference images in each emotional state folder
   - Images should be clear photos of the person in that emotional state

5. **Add training videos** (optional):
   - Place video files in the main persona folder
   - Name them according to the `video_files` list in metadata.json

6. **Run persona upload**:
   ```bash
   python scripts/upload_persona.py
   ```

## File Structure
```
personas/your_persona_name/
├── metadata.json              # Persona configuration
├── reference_frames/          # Reference images for video generation
│   ├── angry/                # Images showing angry expression
│   ├── inspired/             # Images showing inspired expression  
│   ├── neutral/              # Images showing neutral expression
│   ├── reflective/           # Images showing reflective expression
│   └── relief/               # Images showing relief expression
├── videos/                   # Generated videos (auto-created)
├── embeddings/              # AI embeddings (auto-created)
└── processed/               # Processed data (auto-created)
```