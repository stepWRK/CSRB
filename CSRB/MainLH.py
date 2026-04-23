# Copyright (C) 2026 stepWRK
#
# This file is part of SRBcalculate.
#
# SRBcalculate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from gui import MainWindow # оно работает и запускает остальное, не трогать!!!
if __name__ == "__main__":
    app = MainWindow()
    app.window.mainloop()