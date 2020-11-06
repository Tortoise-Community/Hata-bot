from hata import CLIENTS


class wrapper:
    def commands(self, func, *args, **kwargs):
        for client in CLIENTS:
            client.commands(*args, **kwargs)(func)
        return func

    def events(self, func, *args, **kwargs):
        for client in CLIENTS:
            client.events(*args, **kwargs)(func)
        return func


ALL = wrapper()
