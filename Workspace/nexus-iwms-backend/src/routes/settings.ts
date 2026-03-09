import { Router } from 'express';
import { getSettings, getSetting, updateSetting, deleteSetting } from '../controllers/settingController';
import { authenticate } from '../middleware/auth';
import { authorize } from '../middleware/rbac';

const router = Router();

router.use(authenticate);

router.get('/', authorize(['read_settings']), getSettings);

router.get('/:key', authorize(['read_settings']), getSetting);

router.put('/:key', authorize(['update_settings']), updateSetting);

router.delete('/:key', authorize(['delete_settings']), deleteSetting);

export default router;