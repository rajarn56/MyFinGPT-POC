# MyFinGPT Chat Frontend

React + TypeScript frontend for MyFinGPT Chat application.

## Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Development

The frontend runs on `http://localhost:5173` (or next available port) by default.

### Environment Variables

Create a `.env` file in the frontend directory (optional):

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

**Note**: If you don't create a `.env` file, it defaults to `http://localhost:8000`.

## Running with Mock Server

1. **Start Mock Server** (in a separate terminal):
   ```bash
   cd ../mock_server
   source venv/bin/activate
   python main.py
   ```
   Server runs on `http://localhost:8000`

2. **Start Frontend**:
   ```bash
   npm run dev
   ```
   Frontend runs on `http://localhost:5173` (or next available port)

3. **Open Browser**: Navigate to the URL shown in the terminal (usually `http://localhost:5173`)

## Troubleshooting

### Network Error / Cannot Connect to Server

If you see "Cannot connect to server" error:

1. **Check if mock server is running**:
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status":"healthy",...}`

2. **Restart mock server** if CORS errors occur (after updating CORS config):
   ```bash
   # Stop the server (Ctrl+C) and restart
   python main.py
   ```

3. **Check browser console** (F12) for CORS errors:
   - If you see CORS errors, make sure the mock server includes your frontend port in CORS origins
   - Common Vite ports: 5173, 5174, 5175

4. **Verify API URL**: Check that `VITE_API_BASE_URL` matches where your mock server is running

## Project Structure

```
src/
├── components/          # React components
│   ├── Chat/           # Chat interface components
│   ├── Progress/       # Progress tracking components
│   ├── Results/        # Results display components
│   └── Layout/         # Layout components
├── hooks/              # Custom React hooks
├── services/           # API and WebSocket clients
├── types/              # TypeScript type definitions
└── config/             # Configuration files
```

## Features

- **Chat Interface**: Real-time chat with markdown support
- **Progress Tracking**: WebSocket-based real-time progress updates
- **Results Display**: Analysis reports, visualizations, and agent activity
- **Session Management**: Automatic session creation and persistence
- **Two-Column Layout**: 50/50 split layout as per design

## Mock Server

During development, the frontend connects to a mock server (see `../mock_server/`). The mock server provides static responses matching the actual API structure.

## Testing

```bash
# Run linter
npm run lint

# Build and preview
npm run build
npm run preview
```
