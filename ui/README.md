# YouTube AI Pipeline UI

MVP UI for the YouTube AI Pipeline system.

## Architecture

- **Backend**: FastAPI wrapping existing Python pipeline modules
- **Frontend**: Next.js + TypeScript + Tailwind CSS
- **Storage**: File-based (reuses existing outputs directory)

## Quick Start

### 1. Start the Backend

```bash
cd ui/backend
pip install -e .
python main.py
```

Backend runs at `http://localhost:8000`

### 2. Start the Frontend

```bash
cd ui/frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`

## Backend Endpoints

### Projects
- `POST /projects` - Create new project
- `GET /projects` - List all projects
- `GET /projects/{id}` - Get project details

### Pipeline Actions
- `POST /projects/{id}/generate-concepts` - Generate concept batch
- `POST /projects/{id}/select-concept` - Select winning concept
- `POST /projects/{id}/generate-script` - Generate script
- `POST /projects/{id}/generate-video-prompts` - Generate video prompts

### Data Fetch
- `GET /projects/{id}/concepts` - Get concepts
- `GET /projects/{id}/script` - Get script
- `GET /projects/{id}/video-prompts` - Get video prompts
- `GET /projects/{id}/final-package` - Get final package

## Frontend Flow

1. **Home** - List projects, create new
2. **Project Setup** (`/projects/new`) - Channel brief form
3. **Pipeline** (`/projects/[id]`) - Step-by-step workflow:
   - Generate Concepts
   - Select Concept
   - Generate Script
   - Generate Video Prompts
   - Export Final Package

## Project Storage

Projects are stored in `outputs/{project_id}/`:
- `.project.json` - Metadata
- `brief.json` - Channel brief
- `01_trends.json` - Trend report
- `02_concepts.json` - Concept batch
- `03_selected_concept.json` - Selected concept
- `04_script.json` - Script
- `05_video_prompts.json` - Video prompts
- `final_package.json` - Combined output
