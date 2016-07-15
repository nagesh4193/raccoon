
class DataFrame(object):
    def __init__(self, data=None, columns=None, index=None):
        # setup the data and column names
        # define from dictionary
        if data is None:
            self._data = list()
            if columns:
                # expand to the number of columns
                self._data = [[] for x in range(len(columns))]
                self._columns = columns
            else:
                self._columns = list()
            if index:
                if not columns:
                    raise AttributeError('cannot initialize with index but no columns')
                # pad out to the number of rows
                self._index = index
                self._pad_data(max_len=len(index))
            else:
                self._index = list()
        elif isinstance(data, dict):
            # setup data
            self._data = [x for x in data.values()]
            # setup columns from directory keys
            self._columns = list(data.keys())
            # pad the data
            self._pad_data()
            # setup index
            if index:
                self.index = index
            else:
                self.index = list(range(len(self._data[0])))

        # sort by columns if provided
        if columns:
            self._sort_columns(columns)

    def _sort_columns(self, columns_list):
        if not (all([x in columns_list for x in self._columns]) and all([x in self._columns for x in columns_list])):
            raise AttributeError(
                'columns_list must be all in current columns, and all current columns must be in columns_list')
        new_sort = [self._columns.index(x) for x in columns_list]
        self._data = [self._data[x] for x in new_sort]
        self._columns = [self._columns[x] for x in new_sort]

    def _pad_data(self, max_len=None):
        if not max_len:
            max_len = max([len(x) for x in self._data])
        for i, col in enumerate(self._data):  # TODO: Can this be an list comprehension
            col.extend([None] * (max_len - len(col)))
            # self.data = [x.extend([None] * (max_len - len(x))) for x in self._data]

    @property
    def data(self):
        return self._data

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, columns_list):
        if len(columns_list) != len(self.data):
            raise AttributeError('length of columns_list is not the same as the number of columns')
        self._columns = columns_list

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index_list):
        if len(index_list) != len(self.data[0]):
            raise AttributeError('length of index_list must be the same as the length of the data')
        self._index = index_list

    def loc(self):
        pass

    def iloc(self):
        pass

    def get(self, indexes=None, columns=None):
        # If one value for either indexes or columns then return list, otherwise list of list
        if indexes is None:
            indexes = self._index
        if columns is None:
            columns = self._columns
        # singe index and column
        if (not isinstance(indexes, list)) and (not isinstance(columns, list)):
            return self.get_cell(indexes, columns)

    def get_cell(self, index, column):
        i = self._index.index(index)
        c = self._columns.index(column)
        return self._data[c][i]

    # TODO: make add_row and add_column public?
    def _add_row(self, index):
        self._index.append(index)
        for c, col in enumerate(self._columns):  # TODO: Turn this into list comprehension
            self._data[c].append(None)

    def _add_missing_rows(self, indexes):
        new_indexes = [x for x in indexes if x not in self._index]
        # TODO: Look for a way to eliminate the for loop
        for x in new_indexes:
            self._add_row(x)

    def _add_column(self, column):
        self._columns.append(column)
        self._data.append([None] * len(self._index))

    def set(self, index=None, column=None, values=None):
        if (index is not None) and (column is not None):
            if isinstance(index, list):
                self.set_column(index, column, values)
            else:
                self.set_cell(index, column, values)
        elif (index is not None) and (column is None):
            self.set_row(index, values)
        elif (index is None) and (column is not None):
            self.set_column(index, column, values)
        else:
            raise AttributeError('either or both of index or column must be provided')

    def set_cell(self, index, column, values):
        try:
            i = self._index.index(index)
        except ValueError:
            i = len(self._index)
            self._add_row(index)
        try:
            c = self._columns.index(column)
        except ValueError:
            c = len(self._columns)
            self._add_column(column)
        self._data[c][i] = values

    def set_row(self, index, values):
        try:
            i = self._index.index(index)
        except ValueError:  # new row
            i = len(self._index)
            self._add_row(index)
        if isinstance(values, dict):
            if not (set(values.keys()).issubset(self._columns)):
                raise AttributeError('keys of values are not all in existing columns')
            for c, column in enumerate(self._columns):
                self._data[c][i] = values.get(column, self._data[c][i])
        else:
            raise AttributeError('cannot handle values of this type.')

    def set_column(self, index=None, column=None, values=None):
        try:
            c = self._columns.index(column)
        except ValueError:  # new column
            c = len(self.columns)
            self._add_column(column)
        if index:  # index was provided
            if len(index) == (index.count(True) + index.count(False)):  # boolean list
                if len(index) != len(self._index):
                    raise AttributeError('boolean index list must be same size of existing index')
                if len(values) != index.count(True):
                    raise AttributeError('length of values list must equal number of True entries in index list')
                indexes = [i for i, x in enumerate(index) if x]
                for x, i in enumerate(indexes):
                    self._data[c][i] = values[x]
            else:  # list of index
                if len(values) != len(index):
                    raise AttributeError('length of values and index must be the same.')
                try:  # all index in current index
                    indexes = [self._index.index(x) for x in index]
                except ValueError:  # new rows need to be added
                    self._add_missing_rows(index)
                    indexes = [self._index.index(x) for x in index]
                for x, i in enumerate(indexes):
                    self._data[c][i] = values[x]
        elif isinstance(values, list):  # no index, only values as list
            if len(values) < len(self._index):
                raise AttributeError('values list must be at least as long as current index length.')
            elif len(values) > len(self._index):
                self._data[c] = values
                self._pad_data()
            else:
                self._data[c] = values
        else:
            raise AttributeError('cannot handle values of this type.')

    def __setitem__(self, index, value):
        pass

    def __getitem__(self, index):
        pass

    def to_csv(self, filename):
        pass

    def from_csv(self, filename):
        pass

    def to_pandas(self):
        pass

    def from_pandas(self):
        pass