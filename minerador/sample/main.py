from view_model import ViewModel
import os
import json


token = ""
path = "https://api.github.com/repos/octocat/Hello-World"
path2 = "https://api.github.com/repos/ggpsgeorge/minerador"
path3 = "https://api.github.com/repos/Kfourit/test2"
viewRepository = ViewModel(token)
repository = viewRepository.getRepositoryFromPath(path3)
#print(repository)

#print(json.dumps(repository.__dict__))