from django.db import models

class NaturalKeyManager(models.Manager):
    def get_by_natural_key(self, *args):
        if len(args) == len(self.model._meta.natural_key_field_names):
            natural_key_kwargs = dict(zip(self.model._meta.natural_key_field_names, args))

            return self.get(**natural_key_kwargs)
        else:
            raise ValueError("Expected more arguments than %s" %args)