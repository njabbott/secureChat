# Chat Magic - Frontend

Angular 17 frontend for Chat Magic with a LinkedIn-inspired design.

## Features

- **Chat Interface**: ChatGPT-like conversation UI
- **Space List**: View all Confluence spaces with document counts
- **Indexing Control**: Start/stop indexing with real-time progress
- **PII Warnings**: Visual indicators when PII is detected
- **Source Attribution**: Links to source Confluence documents
- **Responsive Design**: Works on desktop and mobile

## Design System

### Color Palette (LinkedIn-inspired)

- **Primary**: #0a66c2 (LinkedIn Blue)
- **Secondary**: #f3f2ef (Light Gray)
- **Success**: #057642 (Green)
- **Warning**: #f5b800 (Yellow)
- **Error**: #cc1016 (Red)

### Components

- **ChatComponent**: Main chat interface with message history
- **SpaceListComponent**: Displays Confluence spaces
- **ChatHistoryComponent**: Recent conversation history
- **IndexingStatusComponent**: Indexing control and progress

## Setup

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The app will be available at http://localhost:4200

### Build for Production

```bash
# Build the app
npm run build

# Output will be in dist/chat-magic-frontend
```

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   ├── space-list/
│   │   │   ├── chat-history/
│   │   │   └── indexing-status/
│   │   ├── services/
│   │   │   ├── chat.service.ts
│   │   │   ├── confluence.service.ts
│   │   │   └── indexing.service.ts
│   │   ├── models/
│   │   │   ├── chat.model.ts
│   │   │   ├── confluence.model.ts
│   │   │   └── indexing.model.ts
│   │   └── app.component.ts
│   ├── environments/
│   │   └── environment.ts
│   ├── styles.css
│   ├── index.html
│   └── main.ts
├── angular.json
├── package.json
└── tsconfig.json
```

## Configuration

Backend API URL is configured in `src/environments/environment.ts`:

```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};
```

## Development

### Adding New Components

```bash
# Generate a new component
ng generate component components/my-component --standalone
```

### Adding New Services

```bash
# Generate a new service
ng generate service services/my-service
```

## Styling

Global styles are in `src/styles.css` with CSS variables for the LinkedIn color palette:

```css
--primary-color: #0a66c2;
--background-primary: #ffffff;
--text-primary: #000000;
/* ... more variables */
```

Components use these variables for consistent styling.

## API Integration

Services communicate with the backend API:

- **ChatService**: Sends messages and receives responses
- **ConfluenceService**: Fetches space information
- **IndexingService**: Controls indexing and polls for progress

All services use Angular's HttpClient with RxJS observables.

## Features to Add (Future)

- [ ] Chat history persistence
- [ ] Dark mode
- [ ] Markdown rendering in chat messages
- [ ] File upload for documents
- [ ] Multi-language support
- [ ] User authentication

## Testing

```bash
# Run unit tests
npm test

# Run e2e tests
npm run e2e
```

## Deployment

### Docker

The frontend can be served using nginx:

```dockerfile
FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist/chat-magic-frontend /usr/share/nginx/html
```

### AWS S3 + CloudFront

Build and upload to S3 for static hosting:

```bash
npm run build
aws s3 sync dist/chat-magic-frontend s3://your-bucket-name
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### API Connection Issues

Check that:
1. Backend is running on http://localhost:8000
2. CORS is configured correctly in backend
3. `environment.ts` has the correct API URL

### Build Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## License

Proprietary - Chat Magic
