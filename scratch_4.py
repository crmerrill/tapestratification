

# Utilites for processing tape_data to a fully formatted tape_data for cashflow engine use
def _check_required_fields(self, config_data):
    for field in config_data.required_fields:
        if field not in self.tape_data.columns:
            print(f'Required field {field} is not contained in data tape.  Please check data tape fields')
            return False
        else:
            pass
    return True




def import_clean_data(self, tape_file, input_type='csv', delimiter=None, sheet_name=None):
    # look at whether we are getting tape_data from flatfile or SQL.
    if input_type is None:
        input_type = tape_file.split('.')[-1].lower()
    elif input_type.lower() == 'sql':
        return print('SLQ not yet supported.  Write the code or use a flat file format')
        # TODO: Write SQL Code: (1) Check for No Lock in SQL string (2) Test if database exists and connection possible before query (3) run query and put into dataframe (4) enforce strict types
    else:
        # set up delimiter types for flat files:
        delimdict = {'csv': ',',
                     'tsv': '\t',
                     'txt': delimiter
                     }
        delimiter = delimdict[input_type.lower()]

        # get the header information so we know what fields are on the tape_data
        with open(tape_file) as file:
            header = next(csv.reader(file, delimiter=delimiter))
        # TODO: need to adust header names to trim extra space
        # now we will set-up dictinaries of types and converters for pandas to use when reading files to dataframes
        # basic type and converter dictionaries
        typedict = {}
        convertdict = getConverterDict()
        datelist = list(set(assetvars.dates).intersection(header))
        for var in set(header).difference(datelist).difference(convertdict):
            typedict[var] = assetvars.getTypeDict(var)

        # Use pandas to process flat file type being input
        if input_type in ('CSV', 'csv'):
            self.tape_data = pd.read_csv(tape_file, parse_dates=datelist, date_parser=parseLoanDates,
                                         converters=convertdict,
                                         dtype=typedict)
        elif input_type in ('TSV', 'tsv', 'TXT', 'txt'):
            self.tape_data = pd.read_csv(tape_file, delimiter=delimiter, parse_dates=datelist,
                                         date_parser=parseLoanDates,
                                         converters=convertdict, dtype=typedict)
        elif input_type in ('XLS', 'xls'):
            self.tape_data = pd.read_excel(tape_file, sheet_name=sheet_name, parse_dates=datelist,
                                           date_parser=parseLoanDates,
                                           converters=convertdict, dtype=typedict)
        else:
            raise Exception('Unsupported input type.  Use flat file format, MSExcel format, or SQL query')

        return self
