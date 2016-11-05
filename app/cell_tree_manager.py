import os
import sys
import json
import copy
from string import ascii_lowercase as alphabet

from io import StringIO
from IPython.core.interactiveshell import InteractiveShell


class Capturing(list):
    """
    A class to capture stdout
    """
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self


    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout



class History(object):
    """
    A class to store the history of a particular type of object
    """

    pass


class Cell(object):
    """
    A code cell, attached to a kernel
    """
    def __init__(
        self,
        kernel,
        parent_cell=None,
        branch_tag=None,
        cell_type="code"
        ):

        
        self.cell_type = cell_type
        self.source = []
        self.stdout = None
        self.parent = parent_cell
        self.children = []
        self.generate_cell_id(branch_tag)
        if not branch_tag is None:
            new_kernel = InteractiveShell()
            new_kernel.push(kernel.user_ns)
            self.kernel = new_kernel
        else:
            self.kernel = kernel


    def generate_cell_id(self, branch_tag=None):
        if self.parent is None:
            self.cell_id = 'cell-0'
        else:
            parent_id_pieces = self.parent.cell_id.split('-')
            number = int(parent_id_pieces[-1])
            rest   = parent_id_pieces[:-1]
            if branch_tag is None:
                self.cell_id = '-'.join(rest + [str(number+1)])
            else:
                self.cell_id = '-'.join(rest + ['-'.join([str(number), branch_tag]), '0'])




    def splice_newlines(self, lines):
        if not lines: return lines
        return [line + '\n' for line in lines[:-1]] + [lines[-1]]


    def update_from_string(self, string):
        lines = string.split('\n')
        self.source = self.splice_newlines(lines)


    def execute(self):
        with Capturing() as output:
            self.kernel.run_cell('\n'.join(self.source))

        self.stdout = self.splice_newlines(output)


    def render(self):
        d = {
                "id": self.cell_id,
                "cell_type": self.cell_type,
                "source": self.source,
                "outputs": {
                    'stdout': self.stdout
                },
                "parent_id": self.parent.cell_id if not self.parent is None else None,
                "children_id": [child.cell_id for child in self.children] 
            }

        return d


    def spawn(self, n=1):
        assert type(n) is int, "n should be an integer"
        assert n > 0, "n should be a definite positive integer"
        assert n < len(alphabet), \
            'no more than {0} branch_tages are allowed'.format(
                len(alphabet)
                )

        ## Just continue the current kernel in case of single spawn
        if n == 1:
            new_cell = Cell(self.kernel, parent_cell=self)
            self.children.append(new_cell)

        ## Spawn multiple independent kernels
        else:
            for i in range(n):
                new_cell = Cell(
                    self.kernel,
                    parent_cell=self,
                    branch_tag=alphabet[i]
                    )
                self.children.append(new_cell)

        return self.children


    def delete(self):
        if not self.parent is None:
            self.parent.children = self.children
            for child in self.children:
                child.parent = self.parent
        else:
            for child in self.children:
                child.parent = None

        del self



class CellTreeManager(object):
    """
    The backbone of the notebook:
    - Stores the cell tree
    - Keeps a pointer to the root cell
    - Keeps a pointer to the current cell
    - Keeps a path to a location on disk to read from or write to a
      persistified version of the CellTreeManager
    """

    def __init__(self, path=None):
        """
        Constructor
        :path: If not None, create a new notebook. Else, load one from file
        """
        self.path = path
        self.root_kernel = InteractiveShell()
        self.root_cell = Cell(self.root_kernel)
        self.current_cell = self.root_cell
        self.cells = {}
        self.cells[self.root_cell.cell_id] = self.root_cell


    def set_current_cell(self, cell_id):
        self.current_cell = self.cells[cell_id]


    def branch_out(self, n):
        new_cells = self.current_cell.spawn(n)
        for child in new_cells:
            self.cells[child.cell_id] = child
        self.current_cell = new_cells[0]



    def execute(self, n=1):
        self.current_cell.execute()
        if not self.current_cell.children:
            self.branch_out(n)
            self.cells[self.current_cell.cell_id] = self.current_cell
        else:
            self.current_cell = self.current_cell.children[0]


    def render(self):
        cells = {
            cell.cell_id : cell.render()
            for cell in self.cells.values()
        }

        d = {
            "cells": cells,
        }

        return d


    def save(self):
        with open(self.path, 'w') as f:
            f.write(
                json.dumps(
                    self.render(),
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            )
            f.close()


    def load_cells(self, cell, cells_data):
        data = cells_data[cell.cell_id]
        cell.cell_type = data['cell_type']
        cell.source = data['source']
        cell.stdout = data['outputs']['stdout']
        self.cells[cell.cell_id] = cell

        if len(data['children_id']) == 0:
            return

        elif len(data['children_id']) == 1:
            child_cell = Cell(
                cell.kernel,
                parent_cell=cell
                )
            cell.children.append(child_cell)
            self.load_cells(child_cell, cells_data)

        else:
            for i in range(len(data['children_id'])):
                child_cell = Cell(
                    cell.kernel,
                    parent_cell=cell,
                    branch_tag=alphabet[i]
                    )
                cell.children.append(child_cell)
                self.load_cells(child_cell, cells_data)




    def load(self):
        cells_data = json.loads(open(self.path).read())['cells']
        self.load_cells(self.root_cell, cells_data)
