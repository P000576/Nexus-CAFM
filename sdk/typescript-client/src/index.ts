import fetch from 'node-fetch';
import { Building, Employee, Asset, WorkOrder } from './models';

export interface ClientOptions {
  baseUrl?: string;
  token?: string;
}

export class ProjectNexusClient {
  baseUrl: string;
  token?: string;

  constructor(opts: ClientOptions = {}) {
    this.baseUrl = opts.baseUrl ?? 'https://staging.api.project-nexus.example.com/v1';
    this.token = opts.token;
  }

  private headers() {
    const h: Record<string, string> = { 'Content-Type': 'application/json' };
    if (this.token) h['Authorization'] = `Bearer ${this.token}`;
    return h;
  }

  async getBuildings(params: { page?: number; size?: number; q?: string } = {}) {
    const qs = new URLSearchParams();
    if (params.page) qs.set('page', String(params.page));
    if (params.size) qs.set('size', String(params.size));
    if (params.q) qs.set('q', params.q);
    const res = await fetch(`${this.baseUrl}/buildings?${qs.toString()}`, { headers: this.headers() });
    return res.json();
  }

  async createBuilding(b: Building) {
    const res = await fetch(`${this.baseUrl}/buildings`, { method: 'POST', headers: this.headers(), body: JSON.stringify(b) });
    return res.json();
  }

  async updateBuilding(id: string, b: Building) {
    const res = await fetch(`${this.baseUrl}/buildings/${id}`, { method: 'PUT', headers: this.headers(), body: JSON.stringify(b) });
    return res.json();
  }

  async getBuilding(id: string) {
    const res = await fetch(`${this.baseUrl}/buildings/${id}`, { headers: this.headers() });
    return res.json();
  }

  async deleteBuilding(id: string) {
    const res = await fetch(`${this.baseUrl}/buildings/${id}`, { method: 'DELETE', headers: this.headers() });
    return res.status === 204;
  }

  // Employees
  async listEmployees(params: { page?: number; size?: number; department?: string; q?: string } = {}) {
    const qs = new URLSearchParams();
    if (params.page) qs.set('page', String(params.page));
    if (params.size) qs.set('size', String(params.size));
    if (params.department) qs.set('department', params.department);
    if (params.q) qs.set('q', params.q);
    const res = await fetch(`${this.baseUrl}/employees?${qs.toString()}`, { headers: this.headers() });
    return res.json();
  }

  async createEmployee(e: Employee) {
    const res = await fetch(`${this.baseUrl}/employees`, { method: 'POST', headers: this.headers(), body: JSON.stringify(e) });
    return res.json();
  }

  async getEmployee(id: string) {
    const res = await fetch(`${this.baseUrl}/employees/${id}`, { headers: this.headers() });
    return res.json();
  }

  async updateEmployee(id: string, e: Employee) {
    const res = await fetch(`${this.baseUrl}/employees/${id}`, { method: 'PUT', headers: this.headers(), body: JSON.stringify(e) });
    return res.json();
  }

  // Assets
  async getAssets(params: { page?: number; size?: number; roomId?: string; q?: string } = {}) {
    const qs = new URLSearchParams();
    if (params.page) qs.set('page', String(params.page));
    if (params.size) qs.set('size', String(params.size));
    if (params.roomId) qs.set('location.roomId', params.roomId);
    if (params.q) qs.set('q', params.q);
    const res = await fetch(`${this.baseUrl}/assets?${qs.toString()}`, { headers: this.headers() });
    return res.json();
  }

  async createAsset(a: Asset) {
    const res = await fetch(`${this.baseUrl}/assets`, { method: 'POST', headers: this.headers(), body: JSON.stringify(a) });
    return res.json();
  }

  async getAsset(id: string) {
    const res = await fetch(`${this.baseUrl}/assets/${id}`, { headers: this.headers() });
    return res.json();
  }

  async updateAsset(id: string, a: Asset) {
    const res = await fetch(`${this.baseUrl}/assets/${id}`, { method: 'PUT', headers: this.headers(), body: JSON.stringify(a) });
    return res.json();
  }

  async listWorkOrders(params: { page?: number; size?: number; status?: string; assignedTo?: string; q?: string } = {}) {
    const qs = new URLSearchParams();
    if (params.page) qs.set('page', String(params.page));
    if (params.size) qs.set('size', String(params.size));
    if (params.status) qs.set('status', params.status);
    if (params.assignedTo) qs.set('assignedTo', params.assignedTo);
    if (params.q) qs.set('q', params.q);
    const res = await fetch(`${this.baseUrl}/workorders?${qs.toString()}`, { headers: this.headers() });
    return res.json();
  }

  async createWorkOrder(w: WorkOrder) {
    const res = await fetch(`${this.baseUrl}/workorders`, { method: 'POST', headers: this.headers(), body: JSON.stringify(w) });
    return res.json();
  }
}
