import { Request, Response } from 'express';
import Permission from '../models/Permission';

export const getPermissions = async (req: Request, res: Response) => {
  const permissions = await Permission.find();
  res.json(permissions);
};

export const createPermission = async (req: Request, res: Response) => {
  const permission = new Permission(req.body);
  await permission.save();
  res.status(201).json(permission);
};

export const updatePermission = async (req: Request, res: Response) => {
  const permission = await Permission.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(permission);
};

export const deletePermission = async (req: Request, res: Response) => {
  await Permission.findByIdAndDelete(req.params.id);
  res.json({ message: 'Permission deleted' });
};