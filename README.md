# Blueprint MCP

![Blueprint MCP](images/blueprint-mcp.png)

*Image generated using Blueprint MCP, Nano Banana Pro, and Arcade MCP server.*

Diagram generation for understanding codebases and system architecture using Nano Banana Pro.

**Works with Arcade's ecosystem:** Combine with HubSpot, Google Drive, GitHub, and other Arcade tools to extract data from your systems and visualize it as diagrams.

## Setup

### 1. Sign up for Arcade
https://arcade.dev

### 2. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Arcade CLI
pip install arcade-mcp
```

### 3. Login to Arcade
```bash
arcade-mcp login
```

### 4. Get Google AI Studio API Key
https://aistudio.google.com/ → Create API key

### 5. Store Secret in Arcade
```bash
arcade-mcp secret set GOOGLE_API_KEY="your_api_key_here"
```

### 6. Deploy Server
```bash
cd architect_mcp
arcade-mcp deploy
```

### 7. Create Gateway
1. Go to https://api.arcade.dev/dashboard
2. Click "Gateways" → "Create Gateway"
3. Add your deployed `architect_mcp` server to the gateway

### 8. Configure Cursor
1. In Cursor: Settings → MCP
2. Add your Arcade gateway URL
3. Restart Cursor

## Usage

### Tools

- `start_diagram_job` - Start generation, returns job ID
- `check_job_status` - Check if complete
- `download_diagram` - Download PNG as base64

### Example Prompts

**Visualize code architecture:**
```
Analyze the authentication module in src/auth/ and create an 
architecture diagram showing the components and their relationships.
```

**Document API flows:**
```
Create a sequence diagram showing the OAuth login flow based on 
the code in src/auth/oauth.py
```

**Explain processes:**
```
Generate a flowchart explaining how our payment processing works,
showing the steps from checkout to confirmation.
```

**Understand data pipelines:**
```
Create a data flow diagram for our ETL pipeline showing sources,
transformations, and destinations based on the data/ directory.
```

**Combine with other Arcade tools:**
```
Pull the latest deal from HubSpot for "Acme Corp" and create an
architecture diagram of the proposed solution.
```

```
Read the system design doc from Google Drive and generate a 
visual architecture diagram from it.
```

## How It Works

1. `start_diagram_job` → Returns job ID instantly
2. Wait 30 seconds (Nano Banana Pro generates)
3. `check_job_status` → Check if "Complete"
4. `download_diagram` → Get base64 PNG
5. Agent decodes and saves to workspace
