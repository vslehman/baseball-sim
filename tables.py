import sqlite3


ATTRIBUTE_MAP = {
    'ID': 'id',
    'W': 'wins',
    'BB': 'walks',
    'HR': 'home_runs',
    'ERA': 'era',
    '3B': 'triples',
    'AB': 'at_bats',
    'E': 'errors',
    'G': 'games',
    'GS': 'games_started',
    'H': 'hits',
    'L': 'losses',
    'yearID': 'year',
    'R': 'runs',
    '2B': 'doubles',
    'ER': 'earned_runs',
    'SV': 'saves',
    'SO': 'strikeouts',
    'SB': 'stolen_bases',
    'SF': 'sac_flies',
    'RBI': 'rbi',
    'POS': 'position',
    'BFP': 'batters_faced',
}


class SqlLite(object):

    def __init__(self, database_filename):
        self.database_name = database_filename
        self.connection = sqlite3.connect(database_filename)
        self.cursor = self.connection.cursor()
    
    def query(self, cmd):
        return self.cursor.execute(cmd)


sql = SqlLite('lahman-baseball-mysql/lahmansbaseballdb.sqlite')


class QueryRow(object):

    def __init__(self, data):
        self.data = data
        for key, val in self.data.items():
            translated_key = ATTRIBUTE_MAP.get(key, key)
            setattr(self, translated_key, val)


class Table(object):

    def __init__(self, table_name, RowClass=QueryRow):
        self.table_name = table_name
        self.RowClass = RowClass
        self.columns = self._get_columns()

    def all(self):
        result = sql.query("SELECT * FROM '{}';".format(self.table_name))
        return self._create_result_dict(result)
    
    def filter(self, **kwargs):
        filter_args = []
        for key, val in kwargs.items():
            key, operator = self._get_key_and_operator(key)
            value = self._get_value(val)
            arg = "{} {} {}".format(key, operator, value)
            filter_args.append(arg)
        query = "SELECT * FROM '{}' WHERE {};".format(
            self.table_name,
            ' AND '.join(filter_args),
        )
        result = sql.query(query)
        return self._create_result_dict(result)
    
    def _get_key_and_operator(self, key):
        if '__' in key:
            tokens = key.split('__')
            return tokens[0], tokens[1]
        return key, '='
    
    def _get_value(self, value):
        if isinstance(value, (set, list, )):
            return '({})'.format(', '.join("'{}'".format(x) for x in value))
        return "'{}'".format(value)
    
    def _create_result_dict(self, result):
        columns = self.columns
        all_result = []
        for row in result:
            row_dict = {}
            for idx, column_name in enumerate(self.columns):
                row_dict[column_name] = row[idx]
            all_result.append(self.RowClass(row_dict))
        return all_result
    
    def _get_columns(self):
        result = sql.query("""
            SELECT * FROM '{}';
        """.format(self.table_name))
        columns = []
        for row in result.description:
            columns.append(row[0])
        return columns
