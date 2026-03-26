import sys

try:
    import tkinter as _tk
    _tk.Tk().destroy()
    GUI_AVAILABLE = True
except Exception:
    GUI_AVAILABLE = False


def main():
    if GUI_AVAILABLE:
        import tkinter as tk
        from gui import HashBreakerGUI
        root = tk.Tk()
        HashBreakerGUI(root)
        root.mainloop()
    else:
        print("tkinter nu este disponibil pe acest sistem.")
        sys.exit(1)


if __name__ == "__main__":
    main()
