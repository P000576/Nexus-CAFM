export interface Id {
  id: string; // uuid
}

export interface Building {
  id?: string;
  name: string;
  address?: string;
  grossAreaSqm?: number;
  metadata?: Record<string, any>;
  createdAt?: string;
  updatedAt?: string;
}

export interface Floor {
  id?: string;
  buildingId: string;
  level: string;
  grossAreaSqm?: number;
  planFileUrl?: string;
}

export interface Room {
  id?: string;
  floorId: string;
  name: string;
  number?: string;
  areaSqm?: number;
  capacity?: number;
  department?: string;
  metadata?: Record<string, any>;
}

export interface Employee {
  id?: string;
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  department?: string;
  role?: string;
  assignedRoomId?: string;
}

export interface Asset {
  id?: string;
  name: string;
  assetTag?: string;
  manufacturer?: string;
  serialNumber?: string;
  location?: {
    buildingId?: string;
    floorId?: string;
    roomId?: string;
  };
  warrantyExpiry?: string;
  qrCodeUrl?: string;
}

export interface WorkOrder {
  id?: string;
  title: string;
  description?: string;
  status?: string;
  priority?: 'Low' | 'Medium' | 'High' | 'Critical';
  requestedBy?: string;
  assignedTo?: string | null;
  assetId?: string;
  location?: {
    buildingId?: string;
    floorId?: string;
    roomId?: string;
  };
  createdAt?: string;
  dueDate?: string;
  laborCost?: number;
  partsCost?: number;
}
