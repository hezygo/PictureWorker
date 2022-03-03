# -*- encoding: utf-8 -*-
"""
@File        :event.py
@Desc        :事件引擎
@Date        :2022-03-03 10:48
"""

from collections import defaultdict
from time import sleep
from threading import Thread
from queue import Queue,Empty

from constant import EVENT_TIMER

class Event:
    def __init__(self, etype, data = None):
        self.etype = etype
        self.data = data

class EventEngine:
    """
    Event engine distributes event object based on its type
    to those handlers registered.
    
    It also generates timer event by every interval seconds,
    which can be used for timing purpose.
    """    
    def __init__(self, interval = 1):
        self._interval = interval
        self._queue = Queue()
        self._active = False
        self._thread = Thread(target=self._run)
        self._timer = Thread(target=self._run_timer)
        self._handlers = defaultdict(list)
        self._general_handlers = []
        
    def _run(self):
        while self._active:
            try:
                event = self._queue.get(block=True, timeout=1)
                self._process(event)
            except Empty:
                pass

    def _process(self, event):
        if event.etype in self._handlers:
            [handler(event) for handler in self._handlers[event.etype]]

        if self._general_handlers:
            [handler(event) for handler in self._general_handlers]

    def _run_timer(self):
        while self._active:
            sleep(self._interval)
            event = Event(EVENT_TIMER)
            self.put(event)

    def start(self):
        self._active = True
        self._thread.start()
        self._timer.start()

    def stop(self):
        self._active = False
        self._timer.join()
        self._thread.join()

    def put(self, event):
        self._queue.put(event)

    def register(self, etype, handler):
        handler_list = self._handlers[etype]
        if handler not in handler_list:
            handler_list.append(handler)

    def unregister(self, etype, handler):
        handler_list = self._handlers[etype]

        if handler in handler_list:
            handler_list.remove(handler)

        if not handler_list:
            self._handlers.pop(etype)

    def register_general(self, handler):
        if handler not in self._general_handlers:
            self._general_handlers.append(handler)

    def unregister_general(self, handler):
        if handler in self._general_handlers:
            self._general_handlers.remove(handler)
