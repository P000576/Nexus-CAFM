import { Router } from 'express';
import { getPermissions, createPermission, updatePermission, deletePermission } from '../controllers/permissionController';
import { authenticate } from '../middleware/auth';
import { authorize } from '../middleware/rbac';

const router = Router();

router.use(authenticate);

router.get('/', authorize(['read_permissions']), getPermissions);

router.post('/', authorize(['create_permissions']), createPermission);

router.put('/:id', authorize(['update_permissions']), updatePermission);

router.delete('/:id', authorize(['delete_permissions']), deletePermission);

export default router;