__author__ = 'kupr'

class MyRecordSet :
    def __init__(self,rows,head):
        self._rows =  rows
        self._head = head
        self._currecord = 0

    def _nextcurrnet(self):
        self._currecord = self._currecord +1

    def next(self):
        i = self._currecord
        self._nextcurrnet()
        if i < len(self._rows) :
            return self._rows[i]
        else:
            return None

    def first(self):
        self._currecord = 0

    def isEndRows(self):
        return self._currecord < 0 or self._currecord >= len(self._rows)

    def PrintHead(self):
        for x in self._head:
            print(str(self._head.index(x))+' | '+str(x))



    def FieldValue(self,row,fieldname):
        for x in self._head :
            try :
                field = x.name
            except :
                field = x[0]

            if str(field).upper() == str(fieldname).upper() :
                try :
                    return row[self._head.index(x)]
                except :
                    return 'null'
        return 'null'

