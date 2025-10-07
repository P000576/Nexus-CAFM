import { ProjectNexusClient } from './index';

async function main() {
  const client = new ProjectNexusClient({ baseUrl: 'https://staging.api.project-nexus.example.com/v1', token: process.env.PN_TOKEN });
  console.log('Listing buildings...');
  const buildings = await client.getBuildings({ page: 1, size: 5 });
  console.log(JSON.stringify(buildings, null, 2));

  console.log('Creating a building (dry-run example)');
  const res = await client.createBuilding({ name: 'Dev Office', address: '10 Dev Rd' });
  console.log(JSON.stringify(res, null, 2));
}

main().catch(err => { console.error(err); process.exit(1); });
