import { Request, Response, NextFunction } from 'express';

export const authorize = (requiredPermissions: string[]) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ message: 'Authentication required' });
    }
    const user = req.user;
    const userPermissions: string[] = user.roles.flatMap((role: any) => role.permissions.map((p: any) => p.name));
    const hasPermission = requiredPermissions.every(perm => userPermissions.includes(perm));
    if (!hasPermission) {
      return res.status(403).json({ message: 'Insufficient permissions' });
    }
    next();
  };
};