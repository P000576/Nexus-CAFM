import { Request, Response } from 'express';
import Role from '../models/Role';

export const getRoles = async (req: Request, res: Response) => {
  const roles = await Role.find().populate('permissions');
  res.json(roles);
};

export const createRole = async (req: Request, res: Response) => {
  const role = new Role(req.body);
  await role.save();
  res.status(201).json(role);
};

export const updateRole = async (req: Request, res: Response) => {
  const role = await Role.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(role);
};

export const deleteRole = async (req: Request, res: Response) => {
  await Role.findByIdAndDelete(req.params.id);
  res.json({ message: 'Role deleted' });
};