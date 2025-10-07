# Project Nexus TypeScript Client SDK (skeleton)

This is a minimal TypeScript client skeleton for the Project Nexus core API. It provides a small `ProjectNexusClient` wrapper with a handful of convenience methods for common operations.

Usage example:

```ts
import { ProjectNexusClient } from 'project-nexus-client';

const client = new ProjectNexusClient({ baseUrl: 'https://staging.api.project-nexus.example.com/v1', token: process.env.PN_TOKEN });

const buildings = await client.getBuildings({ page: 1, size: 10 });
console.log(buildings);
```

Notes:
- This is a starting point. You may want to generate a full SDK using OpenAPI Generator or expand the models/types.
- Run `npm install` and `npm run build` to compile.
