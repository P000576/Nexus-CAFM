import { Router } from 'express';
import { getUsers, getUser, updateUser, deleteUser } from '../controllers/userController';
import { authenticate } from '../middleware/auth';
import { authorize } from '../middleware/rbac';

const router = Router();

router.use(authenticate);

/**
 * @swagger
 * /api/users:
 *   get:
 *     summary: Get all users
 *     tags: [Users]
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: List of users
 */
router.get('/', authorize(['read_users']), getUsers);

router.get('/:id', authorize(['read_users']), getUser);

router.put('/:id', authorize(['update_users']), updateUser);

router.delete('/:id', authorize(['delete_users']), deleteUser);

export default router;