import json

class SortScrapSearch:
    def __init__(self) -> None:
        self.search = self.getJson()
        self.rejectedSearch = {}
        self.validSearch = {}
    
        self.sortSearch()
    
    
    def getJson(self):
        j = ""
        with open("./files/seLoger1.json", "r") as f:
            j = json.load(f)
        print(j)
        return j
    
    
    def sortSearch(self):
        searchCopy = self.search.copy()
        for key, item in self.search.items():
            if not item["colocation"] and not item["studio"]:
                self.validSearch[key] = item
                del searchCopy[key]
                
        print(searchCopy)
        print("\n\n\n")
        print(self.validSearch)
            
            
if __name__ == "__main__":
    SortScrapSearch()