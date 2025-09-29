# routers.py
class ETLRouter:

    SYSTEM_APPS = ['auth', 'contenttypes', 'sessions', 'admin','internal']

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.SYSTEM_APPS:
            return 'default'
        return 'stage'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.SYSTEM_APPS:
            return 'default'
        return 'stage'

    def allow_relation(self, obj1, obj2, **hints):

        db_obj1 = 'default' if obj1._meta.app_label in self.SYSTEM_APPS else 'stage'
        db_obj2 = 'default' if obj2._meta.app_label in self.SYSTEM_APPS else 'stage'
        if db_obj1 == db_obj2:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label in self.SYSTEM_APPS:
            return db == 'default'

        return db == 'stage'
