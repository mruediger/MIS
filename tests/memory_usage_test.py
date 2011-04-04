#!/usr/bin/python

class SimpleClass(object):
    
    __slots__ = [
        'str0',
        'str1',
        'str2',
        'str3',
        'str4',
        'str5',
        'str6',
        'str7',
        'str8',
        'str9',
        'int0',
        'int1',
        'int2',
        'int3',
        'int4',
        'int5',
        'int6',
        'int7',
        'int8',
        'int9',
        'bla'
    ]

    def __init__(self):
        pass


classes = []

for i in range(1, 100000):
    tmp = SimpleClass()
    for slot in tmp.__slots__:
        if slot.startswith("str"):
            setattr(tmp, slot, "teststring " + slot)
        if slot.startswith("int"):
            setattr(tmp, slot, int(slot.lstrip('int')) * 2)
    classes.append(tmp)
        

ausgabe = input("hallo welt")
