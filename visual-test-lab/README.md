# HexSwitch Visual Test Lab

A visual, interactive web application for testing and visualizing hexagonal architecture services. This is a standalone browser-based tool with a dark mode, cyberpunk-inspired design.

## Features

- **Hexagonal Core Visualization**: Interactive canvas showing the core service with ports and adapter connections
- **Adapter Library**: Draggable adapter components (inbound and outbound)
- **Real-time Logs**: Tabbed interface for logs, events, and traces
- **Scenario Timeline**: Visual timeline showing test scenario execution steps
- **Dark Mode UI**: Cyberpunk-inspired design with glow effects and animations

## Getting Started

### Prerequisites

- Node.js 20+ and npm

### Installation

```bash
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173` (or the port shown in the terminal).

### Build

Build for production:

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

Preview the production build:

```bash
npm run preview
```

## Project Structure

```
visual-test-lab/
├── src/
│   ├── components/       # React components
│   │   ├── TopBar.tsx
│   │   ├── AdapterLibrary.tsx
│   │   ├── HexagonalCanvas.tsx
│   │   ├── CoreHexagon.tsx
│   │   ├── AdapterNode.tsx
│   │   ├── ConnectionLine.tsx
│   │   ├── LogsPanel.tsx
│   │   └── ScenarioTimeline.tsx
│   ├── data/             # Mock data
│   │   ├── mockAdapters.ts
│   │   ├── mockLogs.ts
│   │   └── mockScenarios.ts
│   ├── styles/           # CSS files
│   │   ├── theme.css
│   │   └── globals.css
│   ├── utils/            # Utility functions
│   │   └── hexagonGeometry.ts
│   ├── App.tsx           # Main app component
│   └── main.tsx          # Entry point
└── package.json
```

## Usage

1. **Select Scenario**: Use the dropdown in the top bar to select a test scenario
2. **Run Scenario**: Click the "Run Scenario" button to start execution
3. **View Logs**: Switch between Logs, Events, and Traces tabs in the right panel
4. **Monitor Timeline**: Watch the scenario timeline at the bottom to see step-by-step execution

## Technology Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Lucide React** for icons
- **CSS Variables** for theming
- **SVG** for canvas rendering

## Design

The UI features:
- Dark mode color palette (teal, cyan, magenta, blue accents)
- Glow effects and animations
- Isometric 3D perspective on the canvas
- Responsive grid layout (16:9 aspect ratio optimized)

## License

Part of the HexSwitch project.
