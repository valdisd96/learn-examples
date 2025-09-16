from collections import deque

graph = {}
graph["ME"] = ["Alise", "Bob", "Dilon"]
graph["Alise"] = ["Dilon"]
graph["Bob"] = ["Clar", "Pit", "Tanya"]
graph["Dilon"] = ["Pit", "Martin"]
graph["Clar"] = []
graph["Pit"] = []
graph["Tanya"] = ["Alise"]
graph["Martin"] = []


def person_is_seller(name):
    return name == "Martin"

def search(name):
    search_queue = deque()
    search_queue += graph[name]
    searched = []
    while search_queue:
        person = search_queue.popleft()
        if not person in searched:
            if person_is_seller(person):
                print(person, "mango seller!")
                return True
            else:
                search_queue += graph[person]
                searched.append(person)
    return False

search("ME")

