import csv, mwparserfromhell, sys
from models import *
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

'''
TSV columns:
0 = page_id
1 = page_title
2 = rev_id
3 = rev_timestamp
4 = reference (i.e. the raw text)
'''

def scan(file):
    session = Session()
    entries = []
    print('Loading ' + file)
    with open(file) as f:
        reader = csv.reader(f, delimiter='\t')
        for line in reader:
            if line[0] == 'page_id':
                continue
            page_id = int(line[0])
            rev_id = int(line[2])
            rev_timestamp = line[3]
            raw_string = line[4].encode('utf-8')

            refstring = session.query(RefString)\
                .filter_by(raw_string=raw_string).all()
            if len(refstring) == 0:
                refstring = RefString(
                    page_id=page_id,
                    raw_string=raw_string)
                session.add(refstring)
                session.commit()

                try:
                    parsed = mwparserfromhell.parse(line[4])
                    templates = parsed.filter_templates()
                    for template_number, template in enumerate(templates):
                        for param in template.params:
                            name_and_value = param.replace('\n', ' ').strip().split('=', 1)
                            if len(name_and_value) < 2:
                                continue
                            param_name_string = name_and_value[0].strip()
                            param_value = name_and_value[1].strip()
                            if param_value == '' or param_name_string == '' \
                            or len(param_name_string) > 255:
                                continue

                            refparamname = session.query(RefParamName)\
                                .filter_by(name=param_name_string).all()

                            if len(refparamname) == 0:
                                refparamname = RefParamName(name=param_name_string)
                                session.add(refparamname)
                                session.commit()
                            else:
                                refparamname = refparamname[0]

                            refparamvalue = RefParamValue(
                                refstring_id=refstring.id,
                                refparamname_id=refparamname.id,
                                template_number=template_number,
                                value=param_value.encode('utf-8'))
                            entries.append(refparamvalue)

                except Exception as e:
                    print('Refstring mapping failed: ' + str(e))

            else:
                refstring = refstring[0]

            refrevision = RefRevision(
                rev_id=rev_id,
                page_id=page_id,
                rev_timestamp=rev_timestamp,
                refstring_id=refstring.id)
            entries.append(refrevision)

            if len(entries) >= 2000:
                session.add_all(entries)
                session.commit()
                entries = []

    print('Done loading ' + file)

if __name__ == '__main__':
    file = sys.argv[1]
    scan(file)
