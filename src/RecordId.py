class RecordId:
    def __init__(self, pageId, slotId):
        self.pageId  = pageId
        self.slotIdx = slotId


    def getPageId(self):
        return self.pageId

    def getSlotId(self):
        return self.slotIdx
