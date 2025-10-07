from pnexus_client import ProjectNexusClient


def main():
    client = ProjectNexusClient(token=None)
    print('Listing buildings...')
    resp = client.get_buildings(page=1, size=5)
    print(resp)

    print('Creating building (example)')
    payload = { 'name': 'Dev Office', 'address': '10 Dev Rd' }
    created = client.create_building(payload)
    print(created)

if __name__ == '__main__':
    main()
