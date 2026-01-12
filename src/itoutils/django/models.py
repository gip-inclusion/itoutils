class HasDataChangedMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_old_values()

    def set_old_values(self):
        self._old_values = self.__dict__.copy()

    def has_data_changed(self, fields):
        if self._state.adding:
            return True
        if hasattr(self, "_old_values"):
            for field in fields:
                if getattr(self, field) != self._old_values[field]:
                    return True
        return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.set_old_values()
