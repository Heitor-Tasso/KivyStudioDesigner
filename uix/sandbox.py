__all__ = ['DesignerSandbox', ]

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.sandbox import Sandbox, sandbox

class DesignerSandbox(Sandbox):
    '''DesignerSandbox is subclass of :class:`~kivy.uix.sandbox.Sandbox`
       for use with Kivy Designer. It emits on_getting_exeption event
       when code running in it will raise some exception.
    '''
    __events__ = ('on_getting_exception',)
    
    error_active = False
    '''If True, automatically show the error tab on getting an Exception
    '''

    def __init__(self, **kwargs):
        super(DesignerSandbox, self).__init__(**kwargs)
        self.exception = None
        self.tb = None
        self._context['Builder'] = object.__getattribute__(Builder, '_obj')
        self._context['Clock'] = object.__getattribute__(Clock, '_obj')
        Clock.unschedule(self._clock_sandbox)
        Clock.unschedule(self._clock_sandbox_draw)

    def __exit__(self, _type, value, tb):
        '''Override of __exit__
        '''
        self._context.pop()
        if _type is not None:
            return self.on_exception(value, tb=tb)

    def on_exception(self, exception, tb=None):
        '''Override of on_exception
        '''
        self.exception = exception
        self.tb = tb
        self.dispatch('on_getting_exception')
        return super(DesignerSandbox, self).on_exception(exception, tb)

    def on_getting_exception(self, *args):
        '''Default handler for 'on_getting_exception'
        '''
        pass

    @sandbox
    def _clock_sandbox(self, *args):
        pass

    @sandbox
    def _clock_sandbox_draw(self, *args):
        pass
