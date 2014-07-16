garakta
========================================

tiny components.

features

- utilities
- adapters
- swapping(for testing)

utilities
----------------------------------------

utilities is useful components instance.
registering object instance, and use it.

::

    from garakta import create_registry
    reg = create_registry()


    from abc import ABCMeta, abstractmethod


    class Storage(object):
       __metaclass__ = ABCMeta

       @abstractmethod
       def save(self, data):
            pass


    class FileStorage(Storage):
        def __init__(self, name):
            self.name = name

        def save(self, data):
            with open(self.name, "w") as wf:
                self.write(json.dumps(data))


    class MockStorage(Storage):
        def __init__(self):
            self.data = None

        def save(self, data):
            self.data = data


registering and use it.

::

    # for real application
    reg.utilities.register(Storage, FileStorage("savedata.json"))
    reg[Storage].save({"name": "foo", "age": 20})

    # for test application
    reg.utilities.register(Storage, MockStorage())
    reg[Storage].save({"name": "foo", "age": 20})

utilities validation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When registering utilities, we can validate registered object.

::

    def has_name(registry, target):
        return hasattr(target, "name")

    reg.utilities.validation[Storage].append(has_name)
    reg.utilities.register(Storage, MockStorage())  # ValidationError is raised.

adapters
----------------------------------------------

adapters is transformation feature, from a source to a destination.

adapter is like a method adapted after class definition.

::

    def get_storage_name_for_storage(storage):
        return u"保存場所"  # save point

    def get_storage_name_for_file_storage(storage):
        return u"保存場所: {}".format(s.name)

    reg.adapters.display_name(Storage, get_display_name_for_storage)
    reg.adapters.display_name(FileStorage, get_storage_name_for_file_storage, polimorphic=True)


runtime

::

    reg.adapters(MockStorage()).display_name()  # => 保存場所

Or, adapter is class factory for related object.


::

    class S3UploadWrapper(object):
        def __init__(self, storage, connection):
            self.storage = storage
            self.connection = connection

        def upload(self, data, filename):
            raise NotImplemented

        def save(self, data, filename):
            self.storage.save(data)
            self.upload(data, filename)

    reg.adapters.uploader(Storage, S3UploadWrapper)


runtime

::

    uploader = reg.adapters(reg[Storage]).uploader(connection)
    uploader.save({"foo": "bar"}, "foo.json")
