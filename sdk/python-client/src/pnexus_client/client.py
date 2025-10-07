import requests
from typing import Optional, Dict, Any

class ProjectNexusClient:
    def __init__(self, base_url: str = 'https://staging.api.project-nexus.example.com/v1', token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        self.session.headers.update({'Content-Type': 'application/json'})

    def get_buildings(self, page: int = 1, size: int = 25, q: Optional[str] = None) -> Dict[str, Any]:
        params = {'page': page, 'size': size}
        if q:
            params['q'] = q
        r = self.session.get(f"{self.base_url}/buildings", params=params)
        r.raise_for_status()
        return r.json()

    def create_building(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.post(f"{self.base_url}/buildings", json=payload)
        r.raise_for_status()
        return r.json()

    def update_building(self, building_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.put(f"{self.base_url}/buildings/{building_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def list_workorders(self, page: int = 1, size: int = 25, status: Optional[str] = None, assigned_to: Optional[str] = None, q: Optional[str] = None) -> Dict[str, Any]:
        params = {'page': page, 'size': size}
        if status:
            params['status'] = status
        if assigned_to:
            params['assignedTo'] = assigned_to
        if q:
            params['q'] = q
        r = self.session.get(f"{self.base_url}/workorders", params=params)
        r.raise_for_status()
        return r.json()

    def create_workorder(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.post(f"{self.base_url}/workorders", json=payload)
        r.raise_for_status()
        return r.json()

    def get_workorder(self, workorder_id: str) -> Dict[str, Any]:
        r = self.session.get(f"{self.base_url}/workorders/{workorder_id}")
        r.raise_for_status()
        return r.json()

    def update_workorder(self, workorder_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.put(f"{self.base_url}/workorders/{workorder_id}", json=payload)
        r.raise_for_status()
        return r.json()

    def delete_workorder(self, workorder_id: str) -> bool:
        r = self.session.delete(f"{self.base_url}/workorders/{workorder_id}")
        return r.status_code == 204

    # Employees
    def list_employees(self, page: int = 1, size: int = 25, department: Optional[str] = None, q: Optional[str] = None) -> Dict[str, Any]:
        params = {'page': page, 'size': size}
        if department:
            params['department'] = department
        if q:
            params['q'] = q
        r = self.session.get(f"{self.base_url}/employees", params=params)
        r.raise_for_status()
        return r.json()

    def get_employee(self, employee_id: str) -> Dict[str, Any]:
        r = self.session.get(f"{self.base_url}/employees/{employee_id}")
        r.raise_for_status()
        return r.json()

    def create_employee(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.post(f"{self.base_url}/employees", json=payload)
        r.raise_for_status()
        return r.json()

    def update_employee(self, employee_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.put(f"{self.base_url}/employees/{employee_id}", json=payload)
        r.raise_for_status()
        return r.json()

    # Assets
    def list_assets(self, page: int = 1, size: int = 25, room_id: Optional[str] = None, q: Optional[str] = None) -> Dict[str, Any]:
        params = {'page': page, 'size': size}
        if room_id:
            params['location.roomId'] = room_id
        if q:
            params['q'] = q
        r = self.session.get(f"{self.base_url}/assets", params=params)
        r.raise_for_status()
        return r.json()

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        r = self.session.get(f"{self.base_url}/assets/{asset_id}")
        r.raise_for_status()
        return r.json()

    def create_asset(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.post(f"{self.base_url}/assets", json=payload)
        r.raise_for_status()
        return r.json()

    def update_asset(self, asset_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        r = self.session.put(f"{self.base_url}/assets/{asset_id}", json=payload)
        r.raise_for_status()
        return r.json()
