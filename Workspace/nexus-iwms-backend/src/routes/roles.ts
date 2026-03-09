import { Router } from 'express';
import { getRoles, createRole, updateRole, deleteRole } from '../controllers/roleController';
import { authenticate } from '../middleware/auth';
import { authorize } from '../middleware/rbac';

const router = Router();

router.use(authenticate);

router.get('/', authorize(['read_roles']), getRoles);

router.post('/', authorize(['create_roles']), createRole);

router.put('/:id', authorize(['update_roles']), updateRole);

router.delete('/:id', authorize(['delete_roles']), deleteRole);

export default router;