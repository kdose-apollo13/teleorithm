import json
import tkinter

from vbwise import load


model = {
    'root': {
        'title': 'some title',
        'geometry': '400x300'
    },
}

style = {
    'root': {
        'background': '#aabbcc'
    }
}

tkml = '''
App {
    
    Scrollable {
        
        
    }
}
'''

d = load.tkml_string(tkml)
s = json.dumps(d, indent=2)
print(s)




# root.mainloop()

