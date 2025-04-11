from tkinter import *
from tkinter.font import nametofont


def new(parent):
    root = Canvas(parent)
    hili = Canvas(root)
    hili.config({
            'background': '#333333',
            'width': '9',
            })
    text = Text(root)
    return root


def main():
    root = Tk()
    l = new(root)
    print(l)
    

if __name__ == '__main__':
    main()

