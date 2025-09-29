# routers.py
class ETLRouter:

    SYSTEM_APPS = ['auth', 'contenttypes', 'sessions', 'admin','internal']
    DATA_MART_APPS = ['internal_dm']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.SYSTEM_APPS:
            return 'default'
        elif model._meta.app_label in self.DATA_MART_APPS:
            return 'dm'
        return 'stage'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.SYSTEM_APPS:
            return 'default'
        elif model._meta.app_label in self.DATA_MART_APPS:
            return 'dm'
        return 'stage'

    def allow_relation(self, obj1, obj2, **hints):

        if obj1._meta.app_label in self.SYSTEM_APPS:
            db_obj1 = 'default'
        elif obj1._meta.app_label in self.DATA_MART_APPS:
            db_obj1 = 'dm'
        else:
            db_obj1 = 'stage'

        if obj2._meta.app_label in self.SYSTEM_APPS:
            db_obj2 = 'default'
        elif obj2._meta.app_label in self.DATA_MART_APPS:
            db_obj2 = 'dm'
        else:
            db_obj2 = 'stage'
            
        if db_obj1 == db_obj2:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.SYSTEM_APPS:
            return db == 'default'
        elif app_label in self.DATA_MART_APPS:
            return db == 'dm'

        return db == 'stage'
