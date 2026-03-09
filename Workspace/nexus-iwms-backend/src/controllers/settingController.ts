import { Request, Response } from 'express';
import Setting from '../models/Setting';

export const getSettings = async (req: Request, res: Response) => {
  const settings = await Setting.find();
  res.json(settings);
};

export const getSetting = async (req: Request, res: Response) => {
  const setting = await Setting.findOne({ key: req.params.key });
  if (!setting) return res.status(404).json({ message: 'Setting not found' });
  res.json(setting);
};

export const updateSetting = async (req: Request, res: Response) => {
  const { value, type } = req.body;
  const setting = await Setting.findOneAndUpdate(
    { key: req.params.key },
    { value, type },
    { new: true, upsert: true }
  );
  res.json(setting);
};

export const deleteSetting = async (req: Request, res: Response) => {
  await Setting.findOneAndDelete({ key: req.params.key });
  res.json({ message: 'Setting deleted' });
};