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
