class ObjectNotFoundException(Exception):
    def __int__(self, class_name, id_):
        super().__init__('Object not found')
        self.class_name = class_name
        self.id = id_
