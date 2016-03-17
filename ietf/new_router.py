class DatatrackerRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen replica.
        """
        # print model.__name__
        datatracker_tables = ['Person', 'DocAlias', 'Group']
        if model.__name__ in datatracker_tables or model._meta.app_label == 'auth':
            return 'datatracker'
        return 'default'
    
    def db_for_write(self, model, **hints):
        return 'default'
